# Current handoff — Wayfarer Lite Assignment 2, Part 2

## What works

- Vue accepts five-digit U.S. ZIP input and presents loading, invalid, unresolved, empty, failed, rate-limited, and successful-result states.
- FastAPI resolves the exact requested U.S. ZIP through Geoapify, then searches `accommodation.hotel` places in a 5 km circle around that returned coordinate.
- The live response returns provider names, addresses, place IDs, and coordinates only. The Vue list and Leaflet markers share one selected place.
- Root `.env` is ignored and the backend uses it without exposing the key to Vue.
- The Part 2 saved shortlist persists provider snapshots in local SQLite. A duplicate provider ID leaves one original saved record; an individual remove is confirmed in the browser before deletion.
- Saved provider snapshots now include a backend-generated simulated nightly rate and available-room count. The frontend labels both values as local simulations, not Geoapify provider data. Existing SQLite shortlist rows are upgraded on startup.
- `POST /api/hotel-assistant` now implements the revised Part 2 requirement: OpenRouter-backed LLM SQL proposal, backend validation, read-only SQLite retrieval, then a second grounded-answer LLM call. The UI displays the complete workflow.

## Checked

- `npm install leaflet` after approval: installed Leaflet 1.9.4; npm audit reported no vulnerabilities.
- `certifi` was added after the standard Python TLS store failed to verify Geoapify; all backend unit tests passed after the change.
- `python3 -m unittest discover -s backend/tests -v`: 8 passing tests, including fixed-fixture duplicate, restart-persistence, and removal checks.
- `npm run build` from `frontend/`: production build passed.
- Live check on September 29, 2026: ZIP `02108` resolved to Boston, Massachusetts and returned 20 provider hotel places within the documented 5 km / 20-result limit.
- Manual browser checks recorded in `screenshots/assignment2-part1/`: live list/map results, marker popup, list-to-map selection for Beacon Hill Hotel and Bistro, and invalid ZIP feedback. Those files remain linked in `reports/assignment2-part1/report.md`.
- `test_initialize_upgrades_a_legacy_saved_place_with_local_simulation` proves a pre-simulation SQLite shortlist is upgraded without losing its saved provider record.
- `test_rag_chat.py` uses a fake LLM to verify the two-call planner/retriever/answer flow and rejects writes, other tables, and oversized result limits before SQLite execution.

## Remaining work

- Manually verify the local simulation extension: save a live hotel, record its clearly labeled simulated rate and room count, refresh the browser, and confirm the same saved values are read from SQLite. Do not show the API key.
- Live verification on October 6, 2026: the question “Which saved hotel has the lowest simulated nightly rate, and how many simulated rooms are available?” produced one read-only SELECT, retrieved Fairfield Inn & Suites at `$156.49` and `5` simulated rooms, and returned a grounded answer that labeled both values local simulations. OpenRouter reported `nvidia/nemotron-3-super-120b-a12b:free`.
- Record the RAG workflow using that saved-hotel question. The screen recording must show question, proposed SQL, retrieved records, grounded answer, model, and expected-versus-observed verification. Do not show either API key.
- Add the accessible video link and the Part 2 manual screenshots to the root `report.md` before submission.
