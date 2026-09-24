from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGINS
from .controller import DatabaseController
from .models import BookingCreate, BookingDetail, BookingStatusUpdate, HotelSearchResult


controller = DatabaseController()


@asynccontextmanager
async def lifespan(_: FastAPI):
    controller.initialize()
    yield


app = FastAPI(title="Wayfarer Lite API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


def translate_error(error: Exception) -> HTTPException:
    if isinstance(error, LookupError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/search", response_model=list[HotelSearchResult])
def search_hotels(hotel_name: str = Query(min_length=1, max_length=100)) -> list[HotelSearchResult]:
    return controller.search_hotels(hotel_name)


@app.get("/api/bookings", response_model=list[BookingDetail])
def list_bookings() -> list[BookingDetail]:
    return controller.list_bookings()


@app.post("/api/bookings", response_model=BookingDetail, status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingCreate) -> BookingDetail:
    try:
        return controller.create_booking(payload)
    except (LookupError, ValueError) as error:
        raise translate_error(error) from error


@app.patch("/api/bookings/{booking_id}", response_model=BookingDetail)
def update_booking(booking_id: int, payload: BookingStatusUpdate) -> BookingDetail:
    try:
        return controller.update_booking_status(booking_id, payload.status)
    except (LookupError, ValueError) as error:
        raise translate_error(error) from error


@app.delete("/api/bookings/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(booking_id: int) -> Response:
    try:
        controller.delete_booking(booking_id)
    except LookupError as error:
        raise translate_error(error) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
