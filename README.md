# Wayfarer Lite — Assignment 2, Part 1

Wayfarer Lite is a Vue, FastAPI, and Geoapify application for exploring provider-listed hotel places near a five-digit U.S. ZIP code. The live results appear in a synchronized list and Leaflet map. It is a discovery tool, not a booking system.

## What it does

- Validates a five-digit U.S. ZIP code, including leading zeros.
- Resolves that exact U.S. ZIP with Geoapify before searching hotel-category places within 5 km of the returned point.
- Displays the same provider names, addresses, and coordinates in a selectable list and map.
- Keeps a selected hotel card and marker synchronized and keyboard reachable.
- Clearly distinguishes invalid input, unresolved ZIPs, no nearby results, provider failures, and provider rate limits.
- Does not invent prices, ratings, availability, or booking confirmations.

Geoapify coverage and fields vary. Each search returns at most 20 provider places, so the result list is not an exhaustive hotel inventory.

## Requirements

- Python 3.11 or later
- Node.js 20 or later
- A free Geoapify API key, kept only in local `.env`

## Configure your local API key

Copy the template at the repository root:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your own key:

```env
GEOAPIFY_API_KEY=your-key-here
```

`.env` is ignored by Git. Never commit it, paste a key into source code, or add it to a report or recording. The Geoapify key is used only by FastAPI; the Vue browser application never receives it.

## Run locally

From the repository root, start the backend:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

In a second terminal, start the frontend:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL, normally `http://127.0.0.1:5173`.

If those ports are occupied, use this matching local pair:

```bash
uvicorn app.main:app --app-dir backend --port 8020
```

```bash
cd frontend
VITE_API_BASE_URL=http://127.0.0.1:8020 npm run dev -- --port 5176
```

Then open `http://127.0.0.1:5176`.

## Checks

```bash
python3 -m unittest discover -s backend/tests -v
cd frontend && npm run build
```

See [research notes and mockup](docs/assignment2-part1-research.md), [the design note](docs/design.md), [selected prompts](prompts/selected-prompts.md), and [the current handoff](handoffs/current.md).
