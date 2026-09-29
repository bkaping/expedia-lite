from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from .config import SHORTLIST_DATABASE_PATH
from .models import ShortlistPlaceInput, ShortlistSaveResult, ShortlistedPlace


class ShortlistController:
    """Database controller for persistent saved external-place snapshots."""

    def __init__(self, database_path: Path = SHORTLIST_DATABASE_PATH):
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
                CREATE TABLE IF NOT EXISTS shortlisted_places (
                    provider_place_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    latitude REAL NOT NULL CHECK (latitude BETWEEN -90 AND 90),
                    longitude REAL NOT NULL CHECK (longitude BETWEEN -180 AND 180),
                    saved_at TEXT NOT NULL
                )
                """
            )

    def list_places(self) -> list[ShortlistedPlace]:
        with self.connection() as connection:
            rows = connection.execute(
                """SELECT provider_place_id, name, address, latitude, longitude, saved_at
                FROM shortlisted_places ORDER BY saved_at DESC, provider_place_id"""
            ).fetchall()
        return [self._place_from_row(row) for row in rows]

    def save_place(self, payload: ShortlistPlaceInput) -> ShortlistSaveResult:
        saved_at = datetime.now(UTC).isoformat()
        with self.connection() as connection:
            cursor = connection.execute(
                """INSERT OR IGNORE INTO shortlisted_places
                (provider_place_id, name, address, latitude, longitude, saved_at)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    payload.provider_place_id,
                    payload.name,
                    payload.address,
                    payload.latitude,
                    payload.longitude,
                    saved_at,
                ),
            )
            row = connection.execute(
                """SELECT provider_place_id, name, address, latitude, longitude, saved_at
                FROM shortlisted_places WHERE provider_place_id = ?""",
                (payload.provider_place_id,),
            ).fetchone()
        return ShortlistSaveResult(place=self._place_from_row(row), created=cursor.rowcount == 1)

    def remove_place(self, provider_place_id: str) -> None:
        with self.connection() as connection:
            cursor = connection.execute(
                "DELETE FROM shortlisted_places WHERE provider_place_id = ?",
                (provider_place_id,),
            )
            if cursor.rowcount == 0:
                raise LookupError("Saved place not found.")

    @staticmethod
    def _place_from_row(row: sqlite3.Row) -> ShortlistedPlace:
        return ShortlistedPlace(
            provider_place_id=row["provider_place_id"],
            name=row["name"],
            address=row["address"],
            latitude=row["latitude"],
            longitude=row["longitude"],
            saved_at=datetime.fromisoformat(row["saved_at"]),
        )
