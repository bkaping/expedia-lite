from __future__ import annotations

import json
import re
import sqlite3
import ssl
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi

from .config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from .models import HotelAssistantResponse
from .shortlist import ShortlistController


OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
TRUSTED_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
SAVED_HOTEL_SCHEMA = """Table: shortlisted_places
Columns: provider_place_id (text), name (text), address (text), latitude (real),
longitude (real), simulated_nightly_rate_usd (real), simulated_available_rooms (integer),
saved_at (text)."""


class AssistantConfigurationError(RuntimeError):
    """Raised when a required local LLM setting is missing."""


class LlmRequestError(RuntimeError):
    """Raised when the selected LLM provider cannot complete a request."""


class UnsafeSqlError(ValueError):
    """Raised when a model proposal does not meet local query rules."""


@dataclass(frozen=True)
class LlmCompletion:
    content: str
    model: str


class OpenRouterClient:
    """Minimal backend-only OpenRouter client using the Python standard library."""

    def __init__(self, api_key: str = OPENROUTER_API_KEY, model: str = OPENROUTER_MODEL):
        self.api_key = api_key
        self.model = model

    def complete(self, messages: list[dict[str, str]]) -> LlmCompletion:
        if not self.api_key:
            raise AssistantConfigurationError(
                "The hotel assistant is not configured. Add OPENROUTER_API_KEY to the local .env file, then restart FastAPI."
            )

        payload = json.dumps(
            {"model": self.model, "messages": messages, "temperature": 0}
        ).encode("utf-8")
        request = Request(
            OPENROUTER_CHAT_URL,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "X-OpenRouter-Title": "Wayfarer Lite Assignment 2",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=45, context=TRUSTED_SSL_CONTEXT) as response:  # noqa: S310 - fixed provider URL
                response_payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise LlmRequestError(
                f"The LLM provider returned status {error.code}. Check the selected model and your OpenRouter account limits."
            ) from error
        except (URLError, TimeoutError) as error:
            raise LlmRequestError("The hotel assistant could not reach the LLM provider.") from error
        except json.JSONDecodeError as error:
            raise LlmRequestError("The LLM provider returned an unreadable response.") from error

        try:
            content = response_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as error:
            raise LlmRequestError("The LLM provider returned no chat message.") from error
        if not isinstance(content, str) or not content.strip():
            raise LlmRequestError("The LLM provider returned an empty chat message.")
        return LlmCompletion(content=content.strip(), model=response_payload.get("model", self.model))


class HotelAssistantController:
    """Plan safe SQL, retrieve local saved hotels, then request a grounded answer."""

    def __init__(
        self,
        shortlist_controller: ShortlistController,
        llm_client: OpenRouterClient | None = None,
    ):
        self.shortlist_controller = shortlist_controller
        self.llm_client = llm_client or OpenRouterClient()

    def answer_question(self, question: str) -> HotelAssistantResponse:
        planning_completion = self.llm_client.complete(
            [
                {
                    "role": "system",
                    "content": "You produce SQLite query plans for a hotel assistant. Never answer the traveler directly in this step.",
                },
                {
                    "role": "user",
                    "content": self._planning_prompt(question),
                },
            ]
        )
        proposed_sql = validate_proposed_sql(extract_sql(planning_completion.content))
        records = self._retrieve_records(proposed_sql)

        answering_completion = self.llm_client.complete(
            [
                {
                    "role": "system",
                    "content": "You are a concise hotel decision assistant. Ground every factual claim in the retrieved local records. Clearly call nightly rates and room counts local simulations, never provider facts or bookings.",
                },
                {
                    "role": "user",
                    "content": self._answering_prompt(question, records),
                },
            ]
        )
        return HotelAssistantResponse(
            question=question,
            proposed_sql=proposed_sql,
            records=records,
            answer=answering_completion.content,
            model=answering_completion.model,
        )

    @staticmethod
    def _planning_prompt(question: str) -> str:
        return f"""A traveler asked: {question!r}

{SAVED_HOTEL_SCHEMA}

Propose exactly one SQLite SELECT query that answers the question from saved hotels.
Rules: use only shortlisted_places; use only the listed columns; no JOINs; no comments;
no PRAGMA; no data modification; include LIMIT 20 or less. Output JSON only in this exact shape:
{{"sql":"SELECT ..."}}"""

    @staticmethod
    def _answering_prompt(question: str, records: list[dict[str, Any]]) -> str:
        return f"""Original traveler question: {question}

Retrieved local SQLite records (the complete evidence for this answer):
{json.dumps(records, ensure_ascii=False)}

Give a short actionable answer. If no records were retrieved, say that no saved hotels matched.
Do not invent facts. Call simulated_nightly_rate_usd and simulated_available_rooms local simulations."""

    def _retrieve_records(self, sql: str) -> list[dict[str, Any]]:
        with self.shortlist_controller.connection() as connection:
            connection.set_authorizer(_read_only_shortlist_authorizer)
            rows = connection.execute(sql).fetchall()
        return [dict(row) for row in rows]


def extract_sql(planner_message: str) -> str:
    json_match = re.search(r"\{.*\}", planner_message, re.DOTALL)
    if not json_match:
        raise UnsafeSqlError("The LLM did not return the required JSON SQL proposal.")
    try:
        proposal = json.loads(json_match.group(0))
    except json.JSONDecodeError as error:
        raise UnsafeSqlError("The LLM returned malformed JSON for its SQL proposal.") from error
    sql = proposal.get("sql") if isinstance(proposal, dict) else None
    if not isinstance(sql, str):
        raise UnsafeSqlError("The LLM SQL proposal did not include a SQL string.")
    return sql


def validate_proposed_sql(proposed_sql: str) -> str:
    sql = proposed_sql.strip()
    if not sql or len(sql) > 1500:
        raise UnsafeSqlError("The proposed SQL is empty or too long.")
    if sql.endswith(";"):
        sql = sql[:-1].strip()
    if ";" in sql or "--" in sql or "/*" in sql or "*/" in sql:
        raise UnsafeSqlError("The proposed SQL must be one comment-free statement.")

    normalized = re.sub(r"\s+", " ", sql).upper()
    if not normalized.startswith("SELECT "):
        raise UnsafeSqlError("Only a single SELECT query may be executed.")
    prohibited = (
        "ATTACH",
        "DETACH",
        "PRAGMA",
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "CREATE",
        "REPLACE",
        "VACUUM",
        "LOAD_EXTENSION",
    )
    if any(re.search(rf"\b{word}\b", normalized) for word in prohibited):
        raise UnsafeSqlError("The proposed SQL contains a prohibited operation.")
    if re.search(r"\bJOIN\b", normalized):
        raise UnsafeSqlError("The proposed SQL may not join other tables.")

    table_references = re.findall(r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.IGNORECASE)
    if [table.casefold() for table in table_references] != ["shortlisted_places"]:
        raise UnsafeSqlError("The proposed SQL must read only from shortlisted_places.")

    limit_match = re.search(r"\bLIMIT\s+(\d+)\b", normalized)
    if limit_match and int(limit_match.group(1)) > 20:
        raise UnsafeSqlError("The proposed SQL limit cannot exceed 20 records.")
    if not limit_match:
        sql = f"{sql} LIMIT 20"
    return sql


def _read_only_shortlist_authorizer(
    action: int,
    argument_one: str | None,
    _argument_two: str | None,
    _database_name: str | None,
    _trigger_name: str | None,
) -> int:
    if action == sqlite3.SQLITE_READ:
        return sqlite3.SQLITE_OK if argument_one == "shortlisted_places" else sqlite3.SQLITE_DENY
    if action in {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_FUNCTION}:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY
