from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.models import ShortlistPlaceInput
from app.shortlist import ShortlistController


FIXTURE_PATH = BACKEND_DIR / "data" / "assignment2-shortlist-sample.json"


class ShortlistControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "shortlist.db"
        self.controller = ShortlistController(self.database_path)
        self.controller.initialize()
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.first_place = ShortlistPlaceInput(**fixture["places"][0])
        self.second_place = ShortlistPlaceInput(**fixture["places"][1])

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_save_prevents_duplicates_and_preserves_the_original_snapshot(self) -> None:
        first_save = self.controller.save_place(self.first_place)
        repeated_save = self.controller.save_place(
            self.first_place.model_copy(update={"name": "Changed live provider name"})
        )

        self.assertTrue(first_save.created)
        self.assertFalse(repeated_save.created)
        self.assertEqual(len(self.controller.list_places()), 1)
        self.assertEqual(repeated_save.place.name, "Beacon Hill Hotel and Bistro")
        self.assertGreater(first_save.place.simulated_nightly_rate_usd, 0)
        self.assertGreaterEqual(first_save.place.simulated_available_rooms, 1)
        self.assertEqual(
            first_save.place.simulated_nightly_rate_usd,
            repeated_save.place.simulated_nightly_rate_usd,
        )

    def test_saved_places_survive_reopen_and_can_be_removed(self) -> None:
        self.controller.save_place(self.first_place)
        self.controller.save_place(self.second_place)

        reopened_controller = ShortlistController(self.database_path)
        reopened_controller.initialize()
        self.assertEqual(len(reopened_controller.list_places()), 2)

        reopened_controller.remove_place(self.first_place.provider_place_id)
        self.assertEqual(
            [place.provider_place_id for place in reopened_controller.list_places()],
            [self.second_place.provider_place_id],
        )

    def test_initialize_upgrades_a_legacy_saved_place_with_local_simulation(self) -> None:
        legacy_database_path = Path(self.temporary_directory.name) / "legacy-shortlist.db"
        connection = sqlite3.connect(legacy_database_path)
        connection.execute(
            """CREATE TABLE shortlisted_places (
            provider_place_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            saved_at TEXT NOT NULL
            )"""
        )
        connection.execute(
            """INSERT INTO shortlisted_places
            (provider_place_id, name, address, latitude, longitude, saved_at)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                self.first_place.provider_place_id,
                self.first_place.name,
                self.first_place.address,
                self.first_place.latitude,
                self.first_place.longitude,
                "2026-10-01T12:00:00+00:00",
            ),
        )
        connection.commit()
        connection.close()

        upgraded_controller = ShortlistController(legacy_database_path)
        upgraded_controller.initialize()
        upgraded_place = upgraded_controller.list_places()[0]

        self.assertGreater(upgraded_place.simulated_nightly_rate_usd, 0)
        self.assertGreaterEqual(upgraded_place.simulated_available_rooms, 1)


if __name__ == "__main__":
    unittest.main()
