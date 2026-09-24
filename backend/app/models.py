from __future__ import annotations

from datetime import datetime

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
