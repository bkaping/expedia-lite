from __future__ import annotations

import json
import ssl
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import certifi

from .config import GEOAPIFY_API_KEY
from .models import LiveHotel, LiveHotelSearchResponse, LiveSearchCenter


GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
PLACES_URL = "https://api.geoapify.com/v2/places"
RADIUS_METERS = 5_000
RESULT_LIMIT = 20
TRUSTED_SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


class ZipUnresolvedError(LookupError):
    """Raised only when Geoapify cannot establish the requested U.S. ZIP."""


class ProviderRequestError(RuntimeError):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


JsonFetcher = Callable[[str, dict[str, str]], dict[str, Any]]


class GeoapifyHotelController:
    """Controller that converts Geoapify responses into honest live-hotel models."""

    def __init__(self, api_key: str = GEOAPIFY_API_KEY, fetch_json: JsonFetcher | None = None):
        self.api_key = api_key
        self.fetch_json = fetch_json or self._fetch_json

    def find_hotels(self, zip_code: str) -> LiveHotelSearchResponse:
        if not self.api_key or self.api_key.startswith("PASTE_"):
            raise ProviderRequestError("Geoapify is not configured on this server.", 503)

        center = self._resolve_zip(zip_code)
        places = self.fetch_json(
            PLACES_URL,
            {
                "categories": "accommodation.hotel",
                "filter": f"circle:{center.longitude},{center.latitude},{RADIUS_METERS}",
                "bias": f"proximity:{center.longitude},{center.latitude}",
                "limit": str(RESULT_LIMIT),
                "lang": "en",
                "apiKey": self.api_key,
            },
        )
        return LiveHotelSearchResponse(
            center=center,
            hotels=self._hotels_from_places(places),
            result_limit=RESULT_LIMIT,
            radius_meters=RADIUS_METERS,
        )

    def _resolve_zip(self, zip_code: str) -> LiveSearchCenter:
        data = self.fetch_json(
            GEOCODING_URL,
            {
                "postcode": zip_code,
                "filter": "countrycode:us",
                "format": "json",
                "limit": "10",
                "apiKey": self.api_key,
            },
        )
        for candidate in data.get("results", []):
            postcode = str(candidate.get("postcode", "")).split("-")[0]
            country_code = str(candidate.get("country_code", "")).lower()
            latitude = candidate.get("lat")
            longitude = candidate.get("lon")
            if postcode != zip_code or country_code != "us" or latitude is None or longitude is None:
                continue
            location_bits = [candidate.get("city") or candidate.get("county"), candidate.get("state")]
            label = ", ".join(str(bit) for bit in location_bits if bit) or str(candidate.get("formatted", zip_code))
            return LiveSearchCenter(
                zip_code=zip_code,
                label=label,
                latitude=float(latitude),
                longitude=float(longitude),
            )
        raise ZipUnresolvedError(f"Geoapify could not resolve U.S. ZIP code {zip_code}.")

    @staticmethod
    def _hotels_from_places(data: dict[str, Any]) -> list[LiveHotel]:
        hotels: list[LiveHotel] = []
        seen_place_ids: set[str] = set()
        for feature in data.get("features", []):
            properties = feature.get("properties") or {}
            geometry = feature.get("geometry") or {}
            coordinates = geometry.get("coordinates") or []
            place_id = properties.get("place_id")
            if (
                not place_id
                or place_id in seen_place_ids
                or len(coordinates) < 2
                or not isinstance(coordinates[0], (int, float))
                or not isinstance(coordinates[1], (int, float))
            ):
                continue
            seen_place_ids.add(place_id)
            hotels.append(
                LiveHotel(
                    provider_place_id=str(place_id),
                    name=str(properties.get("name") or "Name not supplied by provider"),
                    address=str(properties.get("formatted") or properties.get("address_line1") or "Address not supplied by provider"),
                    latitude=float(coordinates[1]),
                    longitude=float(coordinates[0]),
                )
            )
        return hotels

    @staticmethod
    def _fetch_json(url: str, params: dict[str, str]) -> dict[str, Any]:
        request = Request(
            f"{url}?{urlencode(params)}",
            headers={"Accept": "application/json", "User-Agent": "Wayfarer-Lite-Assignment-2"},
        )
        try:
            with urlopen(request, timeout=12, context=TRUSTED_SSL_CONTEXT) as response:  # noqa: S310 - fixed provider URL
                return json.load(response)
        except HTTPError as error:
            if error.code == 429:
                raise ProviderRequestError("Geoapify rate limit reached. Please wait and try again.", 429) from error
            raise ProviderRequestError("Geoapify could not complete the request.", 502) from error
        except (URLError, TimeoutError, json.JSONDecodeError) as error:
            raise ProviderRequestError("Geoapify is unavailable right now. Please try again.", 502) from error
