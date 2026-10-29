from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag_chat import LlmCompletion
from app.skills import SkillsController
from app.skills_companion import SkillsCompanionController


class FakeLlmClient:
    def __init__(self, response: str = "Your fictional note is saved. You can choose what happens next."):
        self.response = response
        self.calls: list[list[dict[str, str]]] = []

    def complete(self, messages: list[dict[str, str]]) -> LlmCompletion:
        self.calls.append(messages)
        return LlmCompletion(content=self.response, model="test/model")


class SkillsControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.store = SkillsController(Path(self.temporary_directory.name) / "skills.db")
        self.store.initialize()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_completed_session_persists_and_becomes_optional_usual_skill(self) -> None:
        session = self.store.start_session("paced_breathing", "chosen")
        ended = self.store.finish_session(session.id, "completed", 60)

        history = self.store.history()

        self.assertEqual(ended.outcome, "completed")
        self.assertEqual(ended.active_seconds, 60)
        self.assertEqual(history.usual_skill_id, "paced_breathing")

    def test_stopped_session_is_kept_for_review(self) -> None:
        session = self.store.start_session("paced_breathing", "chosen")
        ended = self.store.finish_session(session.id, "stopped", 9)

        history = self.store.history()

        self.assertEqual(ended.outcome, "stopped")
        self.assertEqual(history.sessions[0].outcome, "stopped")
        self.assertIsNone(history.usual_skill_id)


class SkillsCompanionControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.store = SkillsController(Path(self.temporary_directory.name) / "skills.db")
        self.store.initialize()
        self.session = self.store.start_session("paced_breathing", "chosen")
        self.store.finish_session(self.session.id, "completed", 60)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_fictional_note_and_bounded_response_are_persisted(self) -> None:
        llm = FakeLlmClient()
        response = SkillsCompanionController(self.store, llm).respond(
            self.session.id, "I followed the fictional count."
        )

        self.assertEqual(response.mode, "reply")
        self.assertEqual(response.model, "test/model")
        self.assertEqual(len(llm.calls), 1)
        self.assertIn("paced_breathing", llm.calls[0][1]["content"])
        self.assertEqual({message.role for message in self.store.history().messages}, {"user", "assistant"})

    def test_possible_crisis_text_is_neither_saved_nor_sent_to_model(self) -> None:
        llm = FakeLlmClient()
        response = SkillsCompanionController(self.store, llm).respond(
            self.session.id, "fictional scenario: I want to die"
        )

        messages = self.store.history().messages

        self.assertEqual(response.mode, "safety_route")
        self.assertEqual(llm.calls, [])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].role, "system")
        self.assertNotIn("want to die", messages[0].body)

    def test_unsafe_model_reply_is_replaced_locally(self) -> None:
        response = SkillsCompanionController(
            self.store, FakeLlmClient("You should seek therapy.")
        ).respond(self.session.id, "A fictional note.")

        self.assertEqual(response.model, "local safety fallback")
        self.assertIn("You can choose", response.message)


if __name__ == "__main__":
    unittest.main()
