# Design note — Wayfarer Lite Assignment 2, Part 1

## MVC responsibilities

The Vue view owns the ZIP field, loading and outcome states, hotel cards, Leaflet map, and one shared selected provider place ID. A card selection opens and highlights its marker; a marker selection highlights and focuses its card. Vue never reads the API key or calls Geoapify directly.

FastAPI is the request boundary. `GET /api/live-hotels?zip_code=#####` validates the five-digit input, translates controller outcomes into distinct HTTP responses, and permits only local frontend origins through CORS. The legacy CSV endpoint remains available but is no longer the primary screen.

`GeoapifyHotelController` is the live-data controller. It reads the backend-only key from local `.env`, resolves the exact requested U.S. ZIP code first, and then requests up to 20 `accommodation.hotel` places in a 5 km circle around that returned point. It maps only provider place IDs, names, formatted addresses, and coordinates into Pydantic models. A provider failure remains a failure rather than becoming an empty result.

## Data and interface decisions

Provider results may be incomplete and may change, so the interface identifies them as limited provider data and makes no claim to show every hotel. It deliberately omits unsupported pricing, rating, availability, and booking language. A missing provider name or address gets a plain, honest label.

Leaflet uses OpenStreetMap tiles with visible attribution. The result list uses native buttons, and marker titles plus keyboard-enabled Leaflet markers preserve keyboard access.
