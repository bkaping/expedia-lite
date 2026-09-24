from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGINS
from .csv_search import CsvSearchController
from .models import HotelMatch


controller = CsvSearchController()
app = FastAPI(title="Wayfarer Lite API", version="1.1.0")
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
