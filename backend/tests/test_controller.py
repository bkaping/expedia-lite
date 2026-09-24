from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.config import DATA_DIR
from app.controller import DatabaseController
from app.models import BookingCreate


class DatabaseControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "travel.db"
        self.controller = DatabaseController(database_path, DATA_DIR)
        self.controller.initialize()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_seed_happens_once_and_search_joins_stays(self) -> None:
        self.controller.initialize()
        results = self.controller.search_hotels("harbor")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Harborview Hotel")
        self.assertEqual(len(results[0].stays), 2)
        self.assertEqual(len(self.controller.list_bookings()), 2)

    def test_booking_create_cancel_delete_and_persistence(self) -> None:
        created = self.controller.create_booking(
            BookingCreate(
                user_id=1,
                hotel_id=3,
                trip_id=301,
                guest_name="Alex Morgan",
                guests=2,
            )
        )
        self.assertEqual(created.status, "confirmed")
        self.assertIn(created.id, [booking.id for booking in self.controller.list_bookings()])

        cancelled = self.controller.update_booking_status(created.id, "cancelled")
        self.assertEqual(cancelled.status, "cancelled")
        self.assertIn(created.id, [booking.id for booking in self.controller.list_bookings()])

        self.controller.delete_booking(created.id)
        reopened = DatabaseController(self.controller.database_path, DATA_DIR)
        self.assertNotIn(created.id, [booking.id for booking in reopened.list_bookings()])


if __name__ == "__main__":
    unittest.main()
