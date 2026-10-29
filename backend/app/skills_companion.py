from __future__ import annotations

from .models import ChatbotAnswerResponse, ChatbotQuestionId
from .skills import SkillsController


FACTUAL_ANSWERS = {
    "about": "Stillpoint is a localhost-only coursework prototype for fictional skill practice. It is not therapy or diagnosis.",
    "breathing_timing": "This practice has six fixed cycles: breathe in for four counts and out for six, for 60 active seconds.",
    "stopping": "Yes. You can pause or end the practice at any time. Ending saves a neutral stopped record.",
    "saved_data": "It saves optional profile choices, practice timing and outcomes, and separate journal entries locally.",
    "journal_privacy": "No. Journal entries stay separate in local SQLite and are never sent to the chatbot or a model.",
    "profile_adaptation": "Your profile changes the greeting and cue explanation. It can be edited or reset at any time.",
}


class SkillsCompanionController:
    """Answer a fixed set of factual coursework questions without a model or free-text input."""

    def __init__(self, skills_controller: SkillsController):
        self.skills_controller = skills_controller

    def answer(self, question_id: ChatbotQuestionId) -> ChatbotAnswerResponse:
        if question_id != "my_setup":
            return ChatbotAnswerResponse(message=FACTUAL_ANSWERS[question_id])

        profile = self.skills_controller.profile()
        completed_count = self.skills_controller.completed_practice_count()
        choices = []
        if profile.display_name:
            choices.append(f"the display name {profile.display_name}")
        if profile.cue_style:
            choices.append(f"the {profile.cue_style.replace('_', '-')} cue style")
        if profile.practice_aim:
            choices.append(f"the {profile.practice_aim.replace('_', ' ')} aim")
        saved_choices = ", ".join(choices) if choices else "no optional profile choices"
        practice_label = "practice" if completed_count == 1 else "practices"
        return ChatbotAnswerResponse(
            message=f"Your setup has {saved_choices}. Local history shows {completed_count} completed {practice_label}."
        )


__all__ = ["SkillsCompanionController"]
