from __future__ import annotations

import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.live_search import (
    GEOCODING_URL,
    PLACES_URL,
    GeoapifyHotelController,
    ProviderRequestError,
    ZipUnresolvedError,
)


class LiveHotelControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.calls: list[tuple[str, dict[str, str]]] = []

        def fake_fetch(url: str, params: dict[str, str]) -> dict:
            self.calls.append((url, params))
            if url == GEOCODING_URL:
                return {
                    "results": [
                        {"postcode": "02109", "country_code": "us", "lat": 42.36, "lon": -71.05},
                        {"postcode": "02108", "country_code": "us", "city": "Boston", "state": "Massachusetts", "lat": 42.357, "lon": -71.063},
                    ]
                }
            return {
                "features": [
                    {
                        "properties": {"place_id": "provider-1", "name": "Harbor Hotel", "formatted": "1 Harbor Way, Boston, MA"},
                        "geometry": {"coordinates": [-71.06, 42.36]},
                    },
                    {
                        "properties": {"place_id": "provider-1", "name": "Duplicate"},
                        "geometry": {"coordinates": [-71.05, 42.35]},
                    },
                    {
                        "properties": {"place_id": "provider-2"},
                        "geometry": {"coordinates": [-71.04, 42.34]},
                    },
                    {
                        "properties": {"place_id": "no-coordinate"},
                        "geometry": {"coordinates": []},
                    },
                ]
            }

        self.controller = GeoapifyHotelController(api_key="test-key", fetch_json=fake_fetch)

    def test_resolves_the_exact_us_zip_and_returns_honest_provider_fields(self) -> None:
        response = self.controller.find_hotels("02108")

        self.assertEqual(response.center.zip_code, "02108")
        self.assertEqual(response.center.label, "Boston, Massachusetts")
        self.assertEqual(response.result_limit, 20)
        self.assertEqual(response.radius_meters, 5000)
        self.assertEqual([hotel.provider_place_id for hotel in response.hotels], ["provider-1", "provider-2"])
        self.assertEqual(response.hotels[1].name, "Name not supplied by provider")
        self.assertEqual(response.hotels[1].address, "Address not supplied by provider")

        places_url, places_params = self.calls[1]
        self.assertEqual(places_url, PLACES_URL)
        self.assertEqual(places_params["categories"], "accommodation.hotel")
        self.assertEqual(places_params["filter"], "circle:-71.063,42.357,5000")
        self.assertEqual(places_params["limit"], "20")

    def test_raises_unresolved_when_no_exact_us_zip_is_returned(self) -> None:
        controller = GeoapifyHotelController(
            api_key="test-key",
            fetch_json=lambda _url, _params: {"results": [{"postcode": "90210", "country_code": "ca", "lat": 1, "lon": 2}]},
        )

        with self.assertRaises(ZipUnresolvedError):
            controller.find_hotels("90210")

    def test_preserves_provider_failure_instead_of_returning_empty_results(self) -> None:
        def failed_fetch(_url: str, _params: dict[str, str]) -> dict:
            raise ProviderRequestError("Geoapify rate limit reached. Please wait and try again.", 429)

        controller = GeoapifyHotelController(api_key="test-key", fetch_json=failed_fetch)

        with self.assertRaises(ProviderRequestError) as context:
            controller.find_hotels("02108")
        self.assertEqual(context.exception.status_code, 429)


if __name__ == "__main__":
    unittest.main()
