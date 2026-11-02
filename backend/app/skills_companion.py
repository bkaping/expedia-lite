from __future__ import annotations

import re

from .models import ChatbotAnswerResponse, ChatbotQuestionId
from .rag_chat import AssistantConfigurationError, LlmRequestError, OpenRouterClient
from .skills import SkillsController


FACTUAL_ANSWERS = {
    "about": "Stillpoint is a localhost-only coursework prototype for fictional skill practice. It is not therapy or diagnosis.",
    "breathing_timing": "This practice has six fixed cycles: breathe in for four counts and out for six, for 60 active seconds.",
    "stopping": "Yes. You can pause or end the practice at any time. Ending saves a neutral stopped record.",
    "saved_data": "It saves optional profile choices, practice timing/outcomes, separate journal entries, and any selected model-summary exchange locally.",
    "journal_privacy": "No. Journal entries stay separate in local SQLite and are never sent to the chatbot or a model.",
    "profile_adaptation": "Your profile changes the greeting and cue explanation. It can be edited or reset at any time.",
}
MODEL_QUESTION = "Create a brief practice summary"
MODEL_UNAVAILABLE_REPLY = "The optional model summary is unavailable. Your completed fictional practice is still saved."
UNSAFE_REPLY_PATTERN = re.compile(
    r"\b(diagnos|therapy|therapist|clinician|medical|medicat|treatment|suicid|self[ -]?harm|"
    r"emergency|crisis|should|must|need to)\b",
    re.IGNORECASE,
)


class SkillsCompanionController:
    """Answer fixed prototype questions without accepting any free-text message."""

    def __init__(self, skills_controller: SkillsController, llm_client: OpenRouterClient | None = None):
        self.skills_controller = skills_controller
        self.llm_client = llm_client or OpenRouterClient()

    def answer(
        self, question_id: ChatbotQuestionId, session_id: str | None = None
    ) -> ChatbotAnswerResponse:
        if question_id == "practice_summary":
            return self._model_summary(session_id)
        if question_id != "my_setup":
            return ChatbotAnswerResponse(mode="local", message=FACTUAL_ANSWERS[question_id])

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
            mode="local",
            message=f"Your setup has {saved_choices}. Local history shows {completed_count} completed {practice_label}."
        )

    def _model_summary(self, session_id: str | None) -> ChatbotAnswerResponse:
        if not session_id:
            raise ValueError("Complete a fictional practice before requesting a model summary.")
        session = self.skills_controller.session(session_id)
        if session.outcome != "completed":
            raise ValueError("Complete a fictional practice before requesting a model summary.")

        profile = self.skills_controller.profile()
        completed_count = self.skills_controller.completed_practice_count()
        profile_summary = (
            f"selected cue style: {profile.cue_style or 'standard'}; "
            f"selected practice aim: {profile.practice_aim or 'not provided'}; "
            f"completed paced-breathing sessions: {completed_count}."
        )
        self.skills_controller.save_message(session_id, "user", MODEL_QUESTION)
        try:
            completion = self.llm_client.complete(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are a narrowly bounded coursework-prototype companion. Return one factual, "
                            "plain-text summary of at most 120 characters. Do not diagnose, provide therapy, "
                            "give medical or crisis advice, interpret feelings, or give instructions. Do not "
                            "change or explain a skill. Use nonjudgmental language. Do not claim to know "
                            "anything beyond the explicit profile choices and practice summary supplied."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Fictional completed practice: {session.skill_id}; active seconds: "
                            f"{session.active_seconds}. Explicit local profile and usage summary: "
                            f"{profile_summary}"
                        ),
                    },
                ]
            )
            reply = self._safe_reply(completion.content)
            model = completion.model if reply != MODEL_UNAVAILABLE_REPLY else "local safety fallback"
            mode = "model" if model == completion.model else "fallback"
        except (AssistantConfigurationError, LlmRequestError):
            reply = MODEL_UNAVAILABLE_REPLY
            model = "local model-unavailable fallback"
            mode = "fallback"

        self.skills_controller.save_message(session_id, "assistant", reply, model)
        return ChatbotAnswerResponse(mode=mode, message=reply, model=model)

    @staticmethod
    def _safe_reply(reply: str) -> str:
        normalized = " ".join(reply.split())
        if not normalized or len(normalized) > 120 or UNSAFE_REPLY_PATTERN.search(normalized):
            return MODEL_UNAVAILABLE_REPLY
        return normalized


__all__ = ["SkillsCompanionController"]
