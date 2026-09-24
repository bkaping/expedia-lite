from __future__ import annotations

import csv
from pathlib import Path

from .config import DATA_DIR
from .models import HotelMatch


class CsvSearchController:
    """Reads the Part 1 hotel fixture and returns matching hotel records."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = Path(data_dir)

    def search_hotels(self, hotel_name: str) -> list[HotelMatch]:
        query = hotel_name.strip().casefold()
        if not query:
            return []

        hotels_path = self.data_dir / "hotels.csv"
        with hotels_path.open(newline="", encoding="utf-8-sig") as source:
            rows = csv.DictReader(source)
            matches = [
                HotelMatch(
                    hotel_id=row["hotel_id"],
                    hotel_name=row["hotel_name"],
                    city=row["city"],
                    state=row["state"],
                    nightly_rate_usd=float(row["nightly_rate_usd"]),
                )
                for row in rows
                if query in row["hotel_name"].casefold()
            ]
        return sorted(matches, key=lambda hotel: hotel.hotel_name)
