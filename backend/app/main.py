from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGINS
from .csv_search import CsvSearchController
from .live_search import GeoapifyHotelController, ProviderRequestError, ZipUnresolvedError
from .models import HotelMatch, LiveHotelSearchResponse


controller = CsvSearchController()
live_hotel_controller = GeoapifyHotelController()
app = FastAPI(title="Wayfarer Lite API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
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
