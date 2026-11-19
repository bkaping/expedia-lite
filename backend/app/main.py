from __future__ import annotations

from contextlib import asynccontextmanager
import asyncio
import contextlib

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGINS
from .models import (
    ChatbotAnswerResponse,
    ChatbotQuestionRequest,
    FinishSkillSessionRequest,
    HistoryResponse,
    JournalEntryCreateRequest,
    JournalEntrySaveResponse,
    JournalHistoryResponse,
    SkillSession,
    StartSkillSessionRequest,
    UserProfile,
    UserProfileUpdateRequest,
)
from .skills import SkillSessionNotFound, SkillsController
from .skills_companion import SkillsCompanionController
from .market.routes import router as market_router, store as market_store, feed as market_feed, finalize_candles


skills_controller = SkillsController()
skills_companion_controller = SkillsCompanionController(skills_controller)


@asynccontextmanager
async def lifespan(_: FastAPI):
    skills_controller.initialize()
    market_store.initialize()
    tasks = [asyncio.create_task(market_feed.run()), asyncio.create_task(finalize_candles())]
    try:
        yield
    finally:
        for task in tasks:
            task.cancel()
        for task in tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await task


app = FastAPI(title="Market Workstation and Coursework API", version="4.1.0", lifespan=lifespan)
app.include_router(market_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/sessions", response_model=SkillSession, status_code=status.HTTP_201_CREATED)
def start_skill_session(payload: StartSkillSessionRequest) -> SkillSession:
    return skills_controller.start_session(payload.skill_id, payload.source)


@app.post("/api/sessions/{session_id}/finish", response_model=SkillSession)
def finish_skill_session(session_id: str, payload: FinishSkillSessionRequest) -> SkillSession:
    try:
        return skills_controller.finish_session(session_id, payload.outcome, payload.active_seconds)
    except SkillSessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@app.get("/api/history", response_model=HistoryResponse)
def get_history() -> HistoryResponse:
    return skills_controller.history()


@app.get("/api/profile", response_model=UserProfile)
def get_profile() -> UserProfile:
    return skills_controller.profile()


@app.put("/api/profile", response_model=UserProfile)
def update_profile(payload: UserProfileUpdateRequest) -> UserProfile:
    return skills_controller.update_profile(payload)


@app.delete("/api/profile", response_model=UserProfile)
def clear_profile() -> UserProfile:
    return skills_controller.clear_profile()


@app.get("/api/journal", response_model=JournalHistoryResponse)
def get_journal_entries() -> JournalHistoryResponse:
    return skills_controller.journal_entries()


@app.post("/api/journal", response_model=JournalEntrySaveResponse)
def save_journal_entry(payload: JournalEntryCreateRequest) -> JournalEntrySaveResponse:
    return skills_controller.save_journal_entry(payload.body)


@app.post("/api/chatbot/questions", response_model=ChatbotAnswerResponse)
def answer_chatbot_question(payload: ChatbotQuestionRequest) -> ChatbotAnswerResponse:
    try:
        return skills_companion_controller.answer(payload.question_id, payload.session_id)
    except SkillSessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
