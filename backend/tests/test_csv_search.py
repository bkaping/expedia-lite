from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.config import DATA_DIR
from app.csv_search import CsvSearchController


class CsvSearchControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = CsvSearchController(DATA_DIR)

    def test_case_insensitive_partial_name_search_returns_course_hotel(self) -> None:
        matches = self.controller.search_hotels("harbor")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].hotel_id, "H001")
        self.assertEqual(matches[0].hotel_name, "Harbor Lantern Hotel")
        self.assertEqual(matches[0].nightly_rate_usd, 150.0)

    def test_no_matching_hotel_returns_empty_list(self) -> None:
        self.assertEqual(self.controller.search_hotels("No Such Hotel"), [])


if __name__ == "__main__":
    unittest.main()
