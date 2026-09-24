# Wayfarer Lite — Part 1

Wayfarer Lite is the Part 1 CSV hotel-search application for the Travel Application assignment. It uses a Vue frontend, a FastAPI backend, and the supplied course CSV data.

## What it does

- Lets a user enter a hotel name and select **Search**.
- Displays matching hotels in a table with hotel name, city, state, and nightly rate.
- Shows a clear message when no hotel name matches.

## Requirements

- Python 3.11 or later
- Node.js 20 or later

## Run locally

Open two terminals from the repository root.

Backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the local address printed by Vite, normally `http://127.0.0.1:5173`.

The API defaults to `http://127.0.0.1:8000`. To use another API address, create `frontend/.env.local` with `VITE_API_BASE_URL=http://127.0.0.1:8000` (substitute your address if needed).

## If another local project is already running

Run both commands from this repository, not from a similarly named copy elsewhere. If ports `8000` or `5173` are occupied, use this matched pair instead:

```bash
uvicorn app.main:app --app-dir backend --port 8020
```

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8020 npm run dev -- --port 5176
```

Then open `http://127.0.0.1:5176`. The frontend and backend port values must match.

## Data

The backend reads `backend/data/hotels.csv` directly on every search. The supplied course file contains eight hotels, including Harbor Lantern Hotel, Maple Square Inn, and Metro Garden Hotel. The remaining supplied CSV files are retained for Part 2.

## Checks

```bash
python3 -m unittest discover -s backend/tests -v
cd frontend && npm run build
```

See [the design note](docs/design.md), [selected prompts](prompts/selected-prompts.md), and [current handoff](handoffs/current.md) for project context.
