# Wayfarer Lite

Wayfarer Lite is a local hotel-stay demonstration application for the Travel Application assignment. It uses a Vue frontend, a FastAPI backend, CSV starter fixtures, and a persistent SQLite database.

## What it does

- Searches hotel names and displays each matching hotel with its available stays.
- Creates simulated bookings from a selected stay.
- Lists booking history, cancels a booking without removing it, and deletes a test booking.
- Seeds SQLite exactly once from the CSV files, then reads and writes only SQLite. Browser refreshes and server restarts retain changes.

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
uvicorn app.main:app --app-dir backend --port 8019
```

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8019 npm run dev -- --port 5174
```

Then open `http://127.0.0.1:5174`. The frontend and backend port values must match.

## Data and reset behavior

The first backend startup creates `backend/data/travel.db` and imports the four CSV files in `backend/data/`. Those CSV files are small demo fixtures because course-provided source files were not included in this workspace. Replace their rows with the supplied records before submission, keeping their headers and IDs.

The database is intentionally ignored by Git. Do not delete it in normal use: that preserves new bookings and status changes. To intentionally reset only the local demo database after stopping the backend, delete the specific file `backend/data/travel.db`; the next startup will seed it again from the CSV fixtures.

## Checks

```bash
python3 -m unittest discover -s backend/tests -v
cd frontend && npm run build
```

See [the design note](docs/design.md), [selected prompts](prompts/selected-prompts.md), and [current handoff](handoffs/current.md) for project context.
