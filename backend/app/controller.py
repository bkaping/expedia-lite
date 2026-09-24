from __future__ import annotations

import csv
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from .config import DATA_DIR, DATABASE_PATH
from .models import BookingCreate, BookingDetail, HotelSearchResult, Stay


class DatabaseController:
    """Database controller responsible for all persistent application CRUD."""

    def __init__(self, database_path: Path = DATABASE_PATH, data_dir: Path = DATA_DIR):
        self.database_path = Path(database_path)
        self.data_dir = Path(data_dir)

    @contextmanager
    def connection(self):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        """Create the schema and seed only if no completed seed is recorded."""
        with self.connection() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS hotels (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    country TEXT NOT NULL,
                    description TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS trips (
                    id INTEGER PRIMARY KEY,
                    hotel_id INTEGER NOT NULL REFERENCES hotels(id),
                    check_in TEXT NOT NULL,
                    check_out TEXT NOT NULL,
                    room_type TEXT NOT NULL,
                    available_rooms INTEGER NOT NULL CHECK (available_rooms >= 0),
                    nightly_rate REAL NOT NULL CHECK (nightly_rate >= 0)
                );
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                );
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    hotel_id INTEGER NOT NULL REFERENCES hotels(id),
                    trip_id INTEGER NOT NULL REFERENCES trips(id),
                    guest_name TEXT NOT NULL,
                    guests INTEGER NOT NULL CHECK (guests > 0),
                    status TEXT NOT NULL CHECK (status IN ('confirmed', 'cancelled')),
                    total_price REAL NOT NULL CHECK (total_price >= 0),
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS app_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            seeded = connection.execute(
                "SELECT value FROM app_metadata WHERE key = 'seed_version'"
            ).fetchone()
            if seeded is None:
                self._seed_from_csv(connection)
                connection.execute(
                    "INSERT INTO app_metadata (key, value) VALUES ('seed_version', '1')"
                )

    def _seed_from_csv(self, connection: sqlite3.Connection) -> None:
        self._insert_csv_rows(
            connection,
            "hotels.csv",
            "INSERT INTO hotels (id, name, city, country, description) VALUES (:id, :name, :city, :country, :description)",
        )
        self._insert_csv_rows(
            connection,
            "trips.csv",
            """INSERT INTO trips
            (id, hotel_id, check_in, check_out, room_type, available_rooms, nightly_rate)
            VALUES (:id, :hotel_id, :check_in, :check_out, :room_type, :available_rooms, :nightly_rate)""",
            integer_fields={"id", "hotel_id", "available_rooms"},
            float_fields={"nightly_rate"},
        )
        self._insert_csv_rows(
            connection,
            "users.csv",
            "INSERT INTO users (id, name, email) VALUES (:id, :name, :email)",
        )
        self._insert_csv_rows(
            connection,
            "bookings.csv",
            """INSERT INTO bookings
            (id, user_id, hotel_id, trip_id, guest_name, guests, status, total_price, created_at)
            VALUES (:id, :user_id, :hotel_id, :trip_id, :guest_name, :guests, :status, :total_price, :created_at)""",
            integer_fields={"id", "user_id", "hotel_id", "trip_id", "guests"},
            float_fields={"total_price"},
        )
    def _insert_csv_rows(
        self,
        connection: sqlite3.Connection,
        filename: str,
        statement: str,
        integer_fields: set[str] | None = None,
        float_fields: set[str] | None = None,
    ) -> None:
        csv_path = self.data_dir / filename
        if not csv_path.exists():
            raise FileNotFoundError(f"Required seed file is missing: {csv_path}")
        with csv_path.open(newline="", encoding="utf-8") as source:
            rows = list(csv.DictReader(source))
        integer_fields = integer_fields or {"id"}
        float_fields = float_fields or set()
        for row in rows:
            for field in integer_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            connection.execute(statement, row)

    def search_hotels(self, hotel_name: str) -> list[HotelSearchResult]:
        query = hotel_name.strip()
        if not query:
            return []
        with self.connection() as connection:
            rows = connection.execute(
                """
                SELECT h.id AS hotel_id, h.name, h.city, h.country, h.description,
                       t.id AS trip_id, t.check_in, t.check_out, t.room_type,
                       t.available_rooms, t.nightly_rate
                FROM hotels AS h
                LEFT JOIN trips AS t ON t.hotel_id = h.id
                WHERE lower(h.name) LIKE lower(?)
                ORDER BY h.name, t.check_in
                """,
                (f"%{query}%",),
            ).fetchall()
        grouped: dict[int, dict] = {}
        for row in rows:
            hotel = grouped.setdefault(
                row["hotel_id"],
                {
                    "id": row["hotel_id"],
                    "name": row["name"],
                    "city": row["city"],
                    "country": row["country"],
                    "description": row["description"],
                    "stays": [],
                },
            )
            if row["trip_id"] is not None:
                hotel["stays"].append(
                    Stay(
                        id=row["trip_id"],
                        hotel_id=row["hotel_id"],
                        check_in=row["check_in"],
                        check_out=row["check_out"],
                        room_type=row["room_type"],
                        available_rooms=row["available_rooms"],
                        nightly_rate=row["nightly_rate"],
                    )
                )
        return [HotelSearchResult(**hotel) for hotel in grouped.values()]

    def list_bookings(self) -> list[BookingDetail]:
        with self.connection() as connection:
            rows = connection.execute(self._booking_select() + " ORDER BY b.created_at DESC, b.id DESC").fetchall()
        return [self._booking_from_row(row) for row in rows]

    def create_booking(self, payload: BookingCreate) -> BookingDetail:
        with self.connection() as connection:
            user = connection.execute("SELECT id FROM users WHERE id = ?", (payload.user_id,)).fetchone()
            stay = connection.execute(
                "SELECT * FROM trips WHERE id = ? AND hotel_id = ?",
                (payload.trip_id, payload.hotel_id),
            ).fetchone()
            if user is None:
                raise LookupError("The selected demo traveler does not exist.")
            if stay is None:
                raise LookupError("That stay is unavailable for the selected hotel.")
            if stay["available_rooms"] < 1:
                raise ValueError("That stay is sold out.")
            total = stay["nightly_rate"] * self._number_of_nights(stay["check_in"], stay["check_out"]) * payload.guests
            cursor = connection.execute(
                """INSERT INTO bookings
                (user_id, hotel_id, trip_id, guest_name, guests, status, total_price, created_at)
                VALUES (?, ?, ?, ?, ?, 'confirmed', ?, ?)""",
                (
                    payload.user_id,
                    payload.hotel_id,
                    payload.trip_id,
                    payload.guest_name.strip(),
                    payload.guests,
                    total,
                    datetime.now(UTC).isoformat(),
                ),
            )
            connection.execute("UPDATE trips SET available_rooms = available_rooms - 1 WHERE id = ?", (payload.trip_id,))
            row = connection.execute(self._booking_select() + " WHERE b.id = ?", (cursor.lastrowid,)).fetchone()
        return self._booking_from_row(row)

    def update_booking_status(self, booking_id: int, status: str) -> BookingDetail:
        with self.connection() as connection:
            booking = connection.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,)).fetchone()
            if booking is None:
                raise LookupError("Booking not found.")
            if booking["status"] == status:
                row = connection.execute(self._booking_select() + " WHERE b.id = ?", (booking_id,)).fetchone()
                return self._booking_from_row(row)
            if status == "confirmed":
                available = connection.execute("SELECT available_rooms FROM trips WHERE id = ?", (booking["trip_id"],)).fetchone()
                if available is None or available["available_rooms"] < 1:
                    raise ValueError("This stay no longer has a room to restore the booking.")
                connection.execute("UPDATE trips SET available_rooms = available_rooms - 1 WHERE id = ?", (booking["trip_id"],))
            elif status == "cancelled":
                connection.execute("UPDATE trips SET available_rooms = available_rooms + 1 WHERE id = ?", (booking["trip_id"],))
            connection.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
            row = connection.execute(self._booking_select() + " WHERE b.id = ?", (booking_id,)).fetchone()
        return self._booking_from_row(row)

    def delete_booking(self, booking_id: int) -> None:
        with self.connection() as connection:
            booking = connection.execute("SELECT trip_id, status FROM bookings WHERE id = ?", (booking_id,)).fetchone()
            if booking is None:
                raise LookupError("Booking not found.")
            if booking["status"] == "confirmed":
                connection.execute("UPDATE trips SET available_rooms = available_rooms + 1 WHERE id = ?", (booking["trip_id"],))
            connection.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))

    @staticmethod
    def _number_of_nights(check_in: str, check_out: str) -> int:
        start = datetime.fromisoformat(check_in)
        end = datetime.fromisoformat(check_out)
        return max((end - start).days, 1)

    @staticmethod
    def _booking_select() -> str:
        return """
            SELECT b.id, b.user_id, b.guest_name, b.guests, b.status, b.total_price, b.created_at,
                   h.id AS hotel_id, h.name AS hotel_name, h.city,
                   t.id AS trip_id, t.check_in, t.check_out, t.room_type
            FROM bookings AS b
            JOIN hotels AS h ON h.id = b.hotel_id
            JOIN trips AS t ON t.id = b.trip_id
        """

    @staticmethod
    def _booking_from_row(row: sqlite3.Row) -> BookingDetail:
        return BookingDetail(
            id=row["id"],
            user_id=row["user_id"],
            guest_name=row["guest_name"],
            guests=row["guests"],
            status=row["status"],
            total_price=row["total_price"],
            created_at=datetime.fromisoformat(row["created_at"]),
            hotel_id=row["hotel_id"],
            hotel_name=row["hotel_name"],
            city=row["city"],
            trip_id=row["trip_id"],
            check_in=row["check_in"],
            check_out=row["check_out"],
            room_type=row["room_type"],
        )
