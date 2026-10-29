from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class HotelMatch(BaseModel):
    hotel_id: str
    hotel_name: str
    city: str
    state: str
    nightly_rate_usd: float


class Stay(BaseModel):
    id: int
    hotel_id: int
    check_in: str
    check_out: str
    room_type: str
    available_rooms: int
    nightly_rate: float


class HotelSearchResult(BaseModel):
    id: int
    name: str
    city: str
    country: str
    description: str
    stays: list[Stay]


class BookingCreate(BaseModel):
    user_id: int = Field(gt=0)
    hotel_id: int = Field(gt=0)
    trip_id: int = Field(gt=0)
    guest_name: str = Field(min_length=2, max_length=100)
    guests: int = Field(ge=1, le=10)


class BookingStatusUpdate(BaseModel):
    status: str = Field(pattern="^(confirmed|cancelled)$")


class BookingDetail(BaseModel):
    id: int
    user_id: int
    guest_name: str
    guests: int
    status: str
    total_price: float
    created_at: datetime
    hotel_id: int
    hotel_name: str
    city: str
    trip_id: int
    check_in: str
    check_out: str
    room_type: str


class LiveSearchCenter(BaseModel):
    zip_code: str
    label: str
    latitude: float
    longitude: float


class LiveHotel(BaseModel):
    provider_place_id: str
    name: str
    address: str
    latitude: float
    longitude: float


class LiveHotelSearchResponse(BaseModel):
    center: LiveSearchCenter
    hotels: list[LiveHotel]
    result_limit: int
    radius_meters: int


class ShortlistPlaceInput(BaseModel):
    provider_place_id: str = Field(min_length=1, max_length=600)
    name: str = Field(min_length=1, max_length=300)
    address: str = Field(min_length=1, max_length=600)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class ShortlistedPlace(ShortlistPlaceInput):
    simulated_nightly_rate_usd: float = Field(gt=0)
    simulated_available_rooms: int = Field(ge=1)
    saved_at: datetime


class ShortlistSaveResult(BaseModel):
    place: ShortlistedPlace
    created: bool


class HotelAssistantRequest(BaseModel):
    question: str = Field(min_length=2, max_length=500)


class HotelAssistantResponse(BaseModel):
    question: str
    proposed_sql: str
    records: list[dict[str, Any]]
    answer: str
    model: str


# Assignment 3 models. The Assignment 2 models above remain available for the
# preserved course artifacts; the active API uses the models below.
SkillId = Literal["paced_breathing"]
SessionSource = Literal["chosen", "usual_skill"]
SessionOutcome = Literal["active", "completed", "stopped"]


class StartSkillSessionRequest(BaseModel):
    skill_id: SkillId
    source: SessionSource


class FinishSkillSessionRequest(BaseModel):
    outcome: Literal["completed", "stopped"]
    active_seconds: int = Field(ge=0, le=3600)


class SkillSession(BaseModel):
    id: str
    skill_id: SkillId
    source: SessionSource
    outcome: SessionOutcome
    active_seconds: int | None = Field(default=None, ge=0)
    started_at: datetime
    ended_at: datetime | None = None


class ConversationMessage(BaseModel):
    id: int
    session_id: str
    role: Literal["user", "assistant", "system"]
    body: str
    model: str | None = None
    created_at: datetime


class HistoryResponse(BaseModel):
    usual_skill_id: SkillId | None = None
    sessions: list[SkillSession]
    messages: list[ConversationMessage]


class CompanionRequest(BaseModel):
    session_id: str = Field(min_length=8, max_length=64)
    message: str = Field(min_length=1, max_length=320)


class CompanionResponse(BaseModel):
    mode: Literal["reply", "safety_route"]
    message: str
    model: str | None = None
