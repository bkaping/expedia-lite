from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.models import ShortlistPlaceInput
from app.rag_chat import HotelAssistantController, LlmCompletion, UnsafeSqlError, validate_proposed_sql
from app.shortlist import ShortlistController


FIXTURE_PATH = BACKEND_DIR / "data" / "assignment2-shortlist-sample.json"


class FakeLlmClient:
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.messages: list[list[dict[str, str]]] = []

    def complete(self, messages: list[dict[str, str]]) -> LlmCompletion:
        self.messages.append(messages)
        return LlmCompletion(content=self.responses.pop(0), model="test/free-model")


class HotelAssistantControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "shortlist.db"
        self.shortlist_controller = ShortlistController(database_path)
        self.shortlist_controller.initialize()
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        self.place = ShortlistPlaceInput(**fixture["places"][0])
        self.shortlist_controller.save_place(self.place)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_plans_retrieves_and_answers_using_saved_hotel_records(self) -> None:
        llm_client = FakeLlmClient(
            [
                json.dumps(
                    {
                        "sql": "SELECT name, simulated_nightly_rate_usd, simulated_available_rooms "
                        "FROM shortlisted_places WHERE name LIKE '%Beacon%' LIMIT 5"
                    }
                ),
                "Beacon Hill Hotel and Bistro is a saved option. Its nightly rate and room count are local simulations.",
            ]
        )
        controller = HotelAssistantController(self.shortlist_controller, llm_client)

        response = controller.answer_question("Which saved Beacon hotel has rooms available?")

        self.assertEqual(response.question, "Which saved Beacon hotel has rooms available?")
        self.assertIn("SELECT name", response.proposed_sql)
        self.assertEqual(response.records[0]["name"], "Beacon Hill Hotel and Bistro")
        self.assertIn("local simulations", response.answer)
        self.assertEqual(response.model, "test/free-model")
        self.assertEqual(len(llm_client.messages), 2)
        self.assertIn("Which saved Beacon hotel", llm_client.messages[1][1]["content"])
        self.assertIn("Beacon Hill Hotel and Bistro", llm_client.messages[1][1]["content"])

    def test_rejects_non_read_only_or_wrong_table_sql(self) -> None:
        with self.assertRaises(UnsafeSqlError):
            validate_proposed_sql("DELETE FROM shortlisted_places")
        with self.assertRaises(UnsafeSqlError):
            validate_proposed_sql("SELECT name FROM sqlite_master")
        with self.assertRaises(UnsafeSqlError):
            validate_proposed_sql("SELECT name FROM shortlisted_places LIMIT 99")


if __name__ == "__main__":
    unittest.main()
