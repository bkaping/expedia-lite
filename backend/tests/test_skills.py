from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.rag_chat import LlmCompletion
from app.models import UserProfileUpdateRequest
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

    def test_optional_profile_is_saved_editable_and_visible_in_history(self) -> None:
        saved = self.store.update_profile(
            UserProfileUpdateRequest(
                display_name="  Avery  ", cue_style="step_by_step", practice_aim="review_pattern"
            )
        )

        history = self.store.history()
        reset = self.store.clear_profile()

        self.assertEqual(saved.display_name, "Avery")
        self.assertEqual(history.profile.cue_style, "step_by_step")
        self.assertEqual(history.profile.practice_aim, "review_pattern")
        self.assertIsNone(reset.display_name)
        self.assertIsNone(self.store.profile().cue_style)

    def test_optional_fictional_journal_entry_is_saved_locally(self) -> None:
        saved = self.store.save_journal_entry("I wrote a fictional coursework journal entry.")

        entries = self.store.journal_entries().entries

        self.assertEqual(saved.mode, "saved")
        self.assertEqual(entries[0].body, "I wrote a fictional coursework journal entry.")

    def test_potentially_urgent_journal_text_is_not_saved(self) -> None:
        response = self.store.save_journal_entry("fictional scenario: I want to die")

        self.assertEqual(response.mode, "safety_route")
        self.assertIsNone(response.entry)
        self.assertEqual(self.store.journal_entries().entries, [])


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
        self.store.update_profile(
            UserProfileUpdateRequest(
                display_name="Avery", cue_style="brief", practice_aim="one_short_practice"
            )
        )
        response = SkillsCompanionController(self.store, llm).respond(
            self.session.id, "I followed the fictional count."
        )

        self.assertEqual(response.mode, "reply")
        self.assertEqual(response.model, "test/model")
        self.assertEqual(len(llm.calls), 1)
        self.assertIn("paced_breathing", llm.calls[0][1]["content"])
        self.assertIn("display name: Avery", llm.calls[0][1]["content"])
        self.assertIn("selected cue style: brief", llm.calls[0][1]["content"])
        self.assertIn("completed paced-breathing sessions: 1", llm.calls[0][1]["content"])
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

    def test_tired_fictional_message_uses_a_local_non_directive_reply(self) -> None:
        llm = FakeLlmClient()

        response = SkillsCompanionController(self.store, llm).respond(self.session.id, "I am tired.")

        self.assertEqual(llm.calls, [])
        self.assertEqual(response.model, "local scripted response")
        self.assertEqual(
            response.message,
            "Thanks for the fictional note. Rest may be one choice to consider; you can choose what happens next.",
        )

    def test_common_website_question_uses_a_local_factual_answer(self) -> None:
        llm = FakeLlmClient()

        response = SkillsCompanionController(self.store, llm).respond(
            self.session.id, "Does the chatbot read my journal?"
        )

        self.assertEqual(llm.calls, [])
        self.assertEqual(response.model, "local scripted response")
        self.assertEqual(
            response.message,
            "No. Journal entries stay separate in local SQLite and are never sent to the chatbot or model.",
        )


if __name__ == "__main__":
    unittest.main()
