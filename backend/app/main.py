from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGINS
from .csv_search import CsvSearchController
from .live_search import GeoapifyHotelController, ProviderRequestError, ZipUnresolvedError
from .models import HotelMatch, LiveHotelSearchResponse, ShortlistPlaceInput, ShortlistSaveResult, ShortlistedPlace
from .shortlist import ShortlistController


controller = CsvSearchController()
live_hotel_controller = GeoapifyHotelController()
shortlist_controller = ShortlistController()


@asynccontextmanager
async def lifespan(_: FastAPI):
    shortlist_controller.initialize()
    yield


app = FastAPI(title="Wayfarer Lite API", version="2.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/search", response_model=list[HotelMatch])
def search_hotels(hotel_name: str = Query(min_length=1, max_length=100)) -> list[HotelMatch]:
    return controller.search_hotels(hotel_name)


@app.get("/api/live-hotels", response_model=LiveHotelSearchResponse)
def search_live_hotels(zip_code: str = Query(pattern=r"^\d{5}$")) -> LiveHotelSearchResponse:
    try:
        return live_hotel_controller.find_hotels(zip_code)
    except ZipUnresolvedError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "zip_unresolved", "message": str(error)},
        ) from error
    except ProviderRequestError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail={"code": "provider_rate_limited" if error.status_code == 429 else "provider_failure", "message": str(error)},
        ) from error


@app.get("/api/shortlist", response_model=list[ShortlistedPlace])
def list_shortlist() -> list[ShortlistedPlace]:
    return shortlist_controller.list_places()


@app.post("/api/shortlist", response_model=ShortlistSaveResult)
def save_to_shortlist(payload: ShortlistPlaceInput) -> ShortlistSaveResult:
    return shortlist_controller.save_place(payload)


@app.delete("/api/shortlist/{provider_place_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_shortlist(provider_place_id: str) -> Response:
    try:
        shortlist_controller.remove_place(provider_place_id)
    except LookupError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
