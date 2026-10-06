# Design note — Wayfarer Lite Assignment 2, Part 2

## MVC responsibilities

The Vue view owns the ZIP field, loading and outcome states, hotel cards, Leaflet map, and one shared selected provider place ID. A card selection opens and highlights its marker; a marker selection highlights and focuses its card. Vue never reads the API key or calls Geoapify directly.

FastAPI is the request boundary. `GET /api/live-hotels?zip_code=#####` validates the five-digit input, translates controller outcomes into distinct HTTP responses, and permits only local frontend origins through CORS. The legacy CSV endpoint remains available but is no longer the primary screen.

`GeoapifyHotelController` is the live-data controller. It reads the backend-only key from local `.env`, resolves the exact requested U.S. ZIP code first, and then requests up to 20 `accommodation.hotel` places in a 5 km circle around that returned point. It maps only provider place IDs, names, formatted addresses, and coordinates into Pydantic models. A provider failure remains a failure rather than becoming an empty result.

`ShortlistController` is the persistence controller. FastAPI exposes `GET /api/shortlist`, `POST /api/shortlist`, and `DELETE /api/shortlist/{provider_place_id}`. The controller stores a saved snapshot in locally generated SQLite: provider place ID (the primary key), provider name, address, latitude, longitude, local simulated nightly rate, local simulated available-room count, and timestamp. The simulations are generated deterministically by the backend when the record is first saved, not supplied by Geoapify. `INSERT OR IGNORE` makes duplicate prevention authoritative in the database and keeps the first stored snapshot recognizable when a later live response changes.

## Data and interface decisions

Provider results may be incomplete and may change, so the interface identifies them as limited provider data and makes no claim to show every hotel. It does not claim provider pricing, rating, availability, or booking information. A missing provider name or address gets a plain, honest label.

Leaflet uses OpenStreetMap tiles with visible attribution. The result list uses native buttons, and marker titles plus keyboard-enabled Leaflet markers preserve keyboard access.

The saved-shortlist section appears separately below the live list/map view. It offers a keyboard-accessible save control per current result, clearly labels saved entries as provider snapshots with local simulations, and asks for confirmation before the destructive remove request. The SQLite file is ignored by Git; the committed fixed JSON sample is used only for repeatable persistence tests.

## Grounded assistant retrieval flow

The assistant is a backend-only, two-call RAG flow over `shortlisted_places`; SQLite retrieval is sufficient because the assignment scope is a small local saved-hotel database. Vue sends one traveler question to `POST /api/hotel-assistant` and renders the returned question, SQL, records, answer, and provider-reported model name.

FastAPI gives the first LLM call the exact saved-hotel schema and rules requiring a one-table `SELECT` query. `HotelAssistantController` parses the JSON proposal, rejects comments, multiple statements, joins, non-`SELECT` commands, other tables, and limits greater than 20. SQLite's authorizer independently permits only reads from `shortlisted_places` while the query runs. The controller then sends the original question plus the exact retrieved records to a second LLM call for a concise, actionable answer. The answer prompt requires local simulated rates and room counts to remain labeled as simulations.
