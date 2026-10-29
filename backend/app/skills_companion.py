from __future__ import annotations

import re

from .models import CompanionResponse
from .rag_chat import AssistantConfigurationError, LlmRequestError, OpenRouterClient
from .skills import SkillsController


CRISIS_PATTERN = re.compile(
    r"\b(suicid(?:e|al)?|kill myself|end my life|self[ -]?harm|hurt myself|want to die|overdose)\b",
    re.IGNORECASE,
)
UNSAFE_REPLY_PATTERN = re.compile(
    r"\b(diagnos|therapy|therapist|clinician|medical|medicat|treatment|suicid|self[ -]?harm|"
    r"emergency|crisis|should|must|need to)\b",
    re.IGNORECASE,
)
FALLBACK_REPLY = "Your fictional note is saved with this practice. You can choose what happens next."


class SkillsCompanionController:
    """Keep the optional post-practice model contribution inside a small, local boundary."""

    def __init__(self, skills_controller: SkillsController, llm_client: OpenRouterClient | None = None):
        self.skills_controller = skills_controller
        self.llm_client = llm_client or OpenRouterClient()

    def respond(self, session_id: str, message: str) -> CompanionResponse:
        session = self.skills_controller.session(session_id)
        if session.outcome != "completed":
            raise ValueError("The optional companion is available only after a completed practice session.")

        cleaned_message = message.strip()
        if CRISIS_PATTERN.search(cleaned_message):
            # Do not send or preserve potential-crisis text. The browser's
            # static crisis route is available independently of this endpoint.
            self.skills_controller.save_message(
                session_id,
                "system",
                "Potentially urgent fictional input was received; its text was not saved or sent to the model.",
            )
            return CompanionResponse(
                mode="safety_route",
                message="This note was not sent to the companion. Crisis support remains available in the fixed button.",
            )

        self.skills_controller.save_message(session_id, "user", cleaned_message)
        completion = self.llm_client.complete(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a narrowly bounded coursework-prototype companion. Return one neutral, plain-text "
                        "acknowledgment of at most 120 characters. Do not diagnose, provide therapy, give medical or "
                        "crisis advice, interpret feelings, or give instructions. Do not alter or explain a skill. "
                        "Use non-judgmental language and make clear that the person can choose their next action."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Fictional practice session: {session.skill_id}. Outcome: {session.outcome}. "
                        f"Optional fictional note: {cleaned_message!r}."
                    ),
                },
            ]
        )
        reply = self._safe_reply(completion.content)
        model = completion.model if reply != FALLBACK_REPLY else "local safety fallback"
        self.skills_controller.save_message(session_id, "assistant", reply, model)
        return CompanionResponse(mode="reply", message=reply, model=model)

    @staticmethod
    def _safe_reply(reply: str) -> str:
        normalized = " ".join(reply.split())
        if not normalized or len(normalized) > 120 or UNSAFE_REPLY_PATTERN.search(normalized):
            return FALLBACK_REPLY
        return normalized


__all__ = ["AssistantConfigurationError", "LlmRequestError", "SkillsCompanionController"]
