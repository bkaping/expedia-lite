from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from .config import SKILLS_DATABASE_PATH
from .models import ConversationMessage, HistoryResponse, SessionSource, SkillId, SkillSession


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
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    body TEXT NOT NULL,
                    model TEXT,
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

    def save_message(self, session_id: str, role: str, body: str, model: str | None = None) -> ConversationMessage:
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
                "SELECT * FROM conversation_messages ORDER BY created_at DESC LIMIT 24"
            ).fetchall()
            usual_row = connection.execute(
                """SELECT skill_id FROM skill_sessions
                WHERE outcome = 'completed' ORDER BY ended_at DESC LIMIT 1"""
            ).fetchone()
        return HistoryResponse(
            usual_skill_id=usual_row["skill_id"] if usual_row else None,
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
    def _message_from_row(row: sqlite3.Row) -> ConversationMessage:
        return ConversationMessage(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            body=row["body"],
            model=row["model"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
