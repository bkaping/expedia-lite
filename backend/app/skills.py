from __future__ import annotations

import re
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from .config import SKILLS_DATABASE_PATH
from .models import (
    ConversationMessage,
    HistoryResponse,
    JournalEntry,
    JournalEntrySaveResponse,
    JournalHistoryResponse,
    SessionSource,
    SkillId,
    SkillSession,
    UserProfile,
    UserProfileUpdateRequest,
)


POTENTIAL_CRISIS_PATTERN = re.compile(
    r"\b(suicid(?:e|al)?|kill myself|end my life|self[ -]?harm|hurt myself|want to die|overdose)\b",
    re.IGNORECASE,
)


class SkillSessionNotFound(LookupError):
    """Raised when a request refers to an unknown practice session."""


class SkillsController:
    """Persist the minimal records required to review fictional practice sessions."""

    def __init__(self, database_path: Path = SKILLS_DATABASE_PATH):
        self.database_path = Path(database_path)

    @contextmanager
    def connection(self):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profile (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    display_name TEXT,
                    cue_style TEXT CHECK (cue_style IN ('brief', 'step_by_step') OR cue_style IS NULL),
                    practice_aim TEXT CHECK (practice_aim IN ('one_short_practice', 'review_pattern') OR practice_aim IS NULL),
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS skill_sessions (
                    id TEXT PRIMARY KEY,
                    skill_id TEXT NOT NULL CHECK (skill_id = 'paced_breathing'),
                    source TEXT NOT NULL CHECK (source IN ('chosen', 'usual_skill')),
                    outcome TEXT NOT NULL CHECK (outcome IN ('active', 'completed', 'stopped')),
                    active_seconds INTEGER CHECK (active_seconds IS NULL OR active_seconds >= 0),
                    started_at TEXT NOT NULL,
                    ended_at TEXT
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES skill_sessions(id),
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    body TEXT NOT NULL,
                    model TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS session_history_order ON skill_sessions(started_at DESC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS conversation_history_order ON conversation_messages(created_at DESC)"
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS journal_history_order ON journal_entries(created_at DESC)"
            )

    def profile(self) -> UserProfile:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM user_profile WHERE singleton = 1").fetchone()
        return self._profile_from_row(row)

    def update_profile(self, payload: UserProfileUpdateRequest) -> UserProfile:
        display_name = " ".join((payload.display_name or "").split()) or None
        if display_name is None and payload.cue_style is None and payload.practice_aim is None:
            return self.clear_profile()

        updated_at = datetime.now(UTC)
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO user_profile (singleton, display_name, cue_style, practice_aim, updated_at)
                VALUES (1, ?, ?, ?, ?)
                ON CONFLICT(singleton) DO UPDATE SET
                    display_name = excluded.display_name,
                    cue_style = excluded.cue_style,
                    practice_aim = excluded.practice_aim,
                    updated_at = excluded.updated_at""",
                (display_name, payload.cue_style, payload.practice_aim, updated_at.isoformat()),
            )
            row = connection.execute("SELECT * FROM user_profile WHERE singleton = 1").fetchone()
        return self._profile_from_row(row)

    def clear_profile(self) -> UserProfile:
        with self.connection() as connection:
            connection.execute("DELETE FROM user_profile WHERE singleton = 1")
        return UserProfile()

    def completed_practice_count(self) -> int:
        with self.connection() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM skill_sessions WHERE outcome = 'completed'"
            ).fetchone()
        return int(row["count"])

    def journal_entries(self) -> JournalHistoryResponse:
        with self.connection() as connection:
            rows = connection.execute(
                "SELECT * FROM journal_entries ORDER BY created_at DESC LIMIT 12"
            ).fetchall()
        return JournalHistoryResponse(entries=[self._journal_entry_from_row(row) for row in rows])

    def save_journal_entry(self, body: str) -> JournalEntrySaveResponse:
        cleaned_body = body.strip()
        if POTENTIAL_CRISIS_PATTERN.search(cleaned_body):
            return JournalEntrySaveResponse(
                mode="safety_route",
                message="This fictional journal entry was not saved. Crisis support remains available in the fixed button.",
            )

        created_at = datetime.now(UTC)
        with self.connection() as connection:
            cursor = connection.execute(
                "INSERT INTO journal_entries (body, created_at) VALUES (?, ?)",
                (cleaned_body, created_at.isoformat()),
            )
            row = connection.execute(
                "SELECT * FROM journal_entries WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        entry = self._journal_entry_from_row(row)
        return JournalEntrySaveResponse(
            mode="saved", message="Fictional journal entry saved locally.", entry=entry
        )

    def start_session(self, skill_id: SkillId, source: SessionSource) -> SkillSession:
        session_id = str(uuid.uuid4())
        started_at = datetime.now(UTC)
        with self.connection() as connection:
            connection.execute(
                """INSERT INTO skill_sessions
                (id, skill_id, source, outcome, active_seconds, started_at, ended_at)
                VALUES (?, ?, ?, 'active', NULL, ?, NULL)""",
                (session_id, skill_id, source, started_at.isoformat()),
            )
        return SkillSession(
            id=session_id,
            skill_id=skill_id,
            source=source,
            outcome="active",
            started_at=started_at,
        )

    def finish_session(self, session_id: str, outcome: str, active_seconds: int) -> SkillSession:
        ended_at = datetime.now(UTC)
        with self.connection() as connection:
            cursor = connection.execute(
                """UPDATE skill_sessions
                SET outcome = ?, active_seconds = ?, ended_at = ?
                WHERE id = ? AND outcome = 'active'""",
                (outcome, active_seconds, ended_at.isoformat(), session_id),
            )
            if cursor.rowcount != 1:
                known_session = connection.execute("SELECT id FROM skill_sessions WHERE id = ?", (session_id,)).fetchone()
                if known_session is None:
                    raise SkillSessionNotFound("That practice session was not found.")
                raise ValueError("That practice session has already ended.")
            row = connection.execute("SELECT * FROM skill_sessions WHERE id = ?", (session_id,)).fetchone()
        return self._session_from_row(row)

    def session(self, session_id: str) -> SkillSession:
        with self.connection() as connection:
            row = connection.execute("SELECT * FROM skill_sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise SkillSessionNotFound("That practice session was not found.")
        return self._session_from_row(row)

    def save_message(
        self, session_id: str, role: str, body: str, model: str | None = None
    ) -> ConversationMessage:
        self.session(session_id)
        created_at = datetime.now(UTC)
        with self.connection() as connection:
            cursor = connection.execute(
                """INSERT INTO conversation_messages (session_id, role, body, model, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (session_id, role, body, model, created_at.isoformat()),
            )
            row = connection.execute(
                "SELECT * FROM conversation_messages WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
        return self._message_from_row(row)

    def history(self) -> HistoryResponse:
        with self.connection() as connection:
            session_rows = connection.execute(
                "SELECT * FROM skill_sessions ORDER BY started_at DESC LIMIT 12"
            ).fetchall()
            message_rows = connection.execute(
                "SELECT * FROM conversation_messages ORDER BY created_at DESC, id DESC LIMIT 12"
            ).fetchall()
            usual_row = connection.execute(
                """SELECT skill_id FROM skill_sessions
                WHERE outcome = 'completed' ORDER BY ended_at DESC LIMIT 1"""
            ).fetchone()
            completed_row = connection.execute(
                "SELECT COUNT(*) AS count FROM skill_sessions WHERE outcome = 'completed'"
            ).fetchone()
            profile_row = connection.execute("SELECT * FROM user_profile WHERE singleton = 1").fetchone()
        return HistoryResponse(
            usual_skill_id=usual_row["skill_id"] if usual_row else None,
            completed_practice_count=int(completed_row["count"]),
            profile=self._profile_from_row(profile_row),
            sessions=[self._session_from_row(row) for row in session_rows],
            messages=[self._message_from_row(row) for row in message_rows],
        )

    @staticmethod
    def _session_from_row(row: sqlite3.Row) -> SkillSession:
        return SkillSession(
            id=row["id"],
            skill_id=row["skill_id"],
            source=row["source"],
            outcome=row["outcome"],
            active_seconds=row["active_seconds"],
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=datetime.fromisoformat(row["ended_at"]) if row["ended_at"] else None,
        )

    @staticmethod
    def _journal_entry_from_row(row: sqlite3.Row) -> JournalEntry:
        return JournalEntry(
            id=row["id"], body=row["body"], created_at=datetime.fromisoformat(row["created_at"])
        )

    @staticmethod
    def _message_from_row(row: sqlite3.Row) -> ConversationMessage:
        return ConversationMessage(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            body=row["body"],
            model=row["model"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    @staticmethod
    def _profile_from_row(row: sqlite3.Row | None) -> UserProfile:
        if row is None:
            return UserProfile()
        return UserProfile(
            display_name=row["display_name"],
            cue_style=row["cue_style"],
            practice_aim=row["practice_aim"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
