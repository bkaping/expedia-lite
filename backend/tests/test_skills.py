from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.models import UserProfileUpdateRequest
from app.skills import SkillsController
from app.skills_companion import SkillsCompanionController


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
    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_common_website_question_returns_a_local_factual_answer(self) -> None:
        response = SkillsCompanionController(self.store).answer("journal_privacy")

        self.assertEqual(
            response.message,
            "No. Journal entries stay separate in local SQLite and are never sent to the chatbot or a model.",
        )

    def test_setup_question_uses_only_saved_profile_and_practice_history(self) -> None:
        self.store.update_profile(
            UserProfileUpdateRequest(
                display_name="Avery", cue_style="brief", practice_aim="one_short_practice"
            )
        )
        session = self.store.start_session("paced_breathing", "chosen")
        self.store.finish_session(session.id, "completed", 60)

        response = SkillsCompanionController(self.store).answer("my_setup")

        self.assertIn("display name Avery", response.message)
        self.assertIn("brief cue style", response.message)
        self.assertIn("one short practice aim", response.message)
        self.assertIn("1 completed practice", response.message)


if __name__ == "__main__":
    unittest.main()
