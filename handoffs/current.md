# Current handoff — Wayfarer Lite Assignment 2, Part 1

## What works

- Vue accepts five-digit U.S. ZIP input and presents loading, invalid, unresolved, empty, failed, rate-limited, and successful-result states.
- FastAPI resolves the exact requested U.S. ZIP through Geoapify, then searches `accommodation.hotel` places in a 5 km circle around that returned coordinate.
- The live response returns provider names, addresses, place IDs, and coordinates only. The Vue list and Leaflet markers share one selected place.
- Root `.env` is ignored and the backend uses it without exposing the key to Vue.

## Checked

- `npm install leaflet` after approval: installed Leaflet 1.9.4; npm audit reported no vulnerabilities.
- `certifi` was added after the standard Python TLS store failed to verify Geoapify; all backend unit tests passed after the change.
- `python3 -m unittest discover -s backend/tests -v`: 5 passing tests.
- `npm run build` from `frontend/`: production build passed.
- Live check on September 29, 2026: ZIP `02108` resolved to Boston, Massachusetts and returned 20 provider hotel places within the documented 5 km / 20-result limit.
- Manual browser checks recorded in `screenshots/assignment2-part1/`: live list/map results, marker popup, list-to-map selection for Beacon Hill Hotel and Bistro, and invalid ZIP feedback.

## Remaining work

- Record the Assignment 2 Part 1 demo and add its accessible link to `report.md`.
- Assignment 2 Part 2 shortlist persistence is deliberately out of scope.
