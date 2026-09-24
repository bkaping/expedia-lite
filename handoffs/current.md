# Current handoff — Wayfarer Lite Part 1

## What works

- Vue accepts a hotel name, displays matching course hotels in a labeled table, and handles no matches.
- FastAPI exposes a hotel-search endpoint.
- The CSV search controller reads the supplied `hotels.csv` data and performs case-insensitive partial-name matching.

## Checked

- `python3 -m unittest discover -s backend/tests -v`
- `npm run build` from `frontend/`
- Browser check on the Part 1 app: `Harbor` returned Harbor Lantern Hotel, and `Atlantis` displayed the required no-results message.

## Remaining limitations and next task

The supplied data are installed. The Part 1 checkpoint is `82d43ec`. Next, capture one successful search and one no-results search, add those screenshot files to the repository, and push the reviewed checkpoint. Part 2 persistence work is intentionally deferred.
