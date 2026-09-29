from __future__ import annotations

import json
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


if __name__ == "__main__":
    unittest.main()
