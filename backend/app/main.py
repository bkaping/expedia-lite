from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGINS
from .models import (
    CompanionRequest,
    CompanionResponse,
    FinishSkillSessionRequest,
    HistoryResponse,
    SkillSession,
    StartSkillSessionRequest,
)
from .skills import SkillSessionNotFound, SkillsController
from .skills_companion import AssistantConfigurationError, LlmRequestError, SkillsCompanionController


skills_controller = SkillsController()
skills_companion_controller = SkillsCompanionController(skills_controller)


@asynccontextmanager
async def lifespan(_: FastAPI):
    skills_controller.initialize()
    yield


app = FastAPI(title="Stillpoint Skills API", version="3.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
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


@app.post("/api/conversations", response_model=CompanionResponse)
def send_companion_message(payload: CompanionRequest) -> CompanionResponse:
    try:
        return skills_companion_controller.respond(payload.session_id, payload.message)
    except SkillSessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    except LlmRequestError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "companion_provider_failure", "message": str(error)},
        ) from error
    except AssistantConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "companion_not_configured", "message": str(error)},
        ) from error
