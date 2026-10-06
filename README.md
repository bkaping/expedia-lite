# Wayfarer Lite — Assignment 2, Part 2: Grounded hotel assistant

Wayfarer Lite is a Vue, FastAPI, and Geoapify application for exploring provider-listed hotel places near a five-digit U.S. ZIP code. The live results appear in a synchronized list and Leaflet map. It is a discovery tool, not a booking system.

## What it does

- Validates a five-digit U.S. ZIP code, including leading zeros.
- Resolves that exact U.S. ZIP with Geoapify before searching hotel-category places within 5 km of the returned point.
- Displays the same provider names, addresses, and coordinates in a selectable list and map.
- Keeps a selected hotel card and marker synchronized and keyboard reachable.
- Clearly distinguishes invalid input, unresolved ZIPs, no nearby results, provider failures, and provider rate limits.
- Lets a user save a returned provider place to a persistent SQLite shortlist, prevents duplicate provider IDs, and removes an individual saved place after confirmation.
- Assigns a saved place a clearly labeled local simulated nightly rate and room availability; it never presents those values as provider prices, real availability, ratings, or booking confirmations.
- Answers questions about the saved shortlist through a grounded two-call LLM workflow: LLM SQL proposal → backend validation/read-only SQLite retrieval → LLM answer based on the retrieved records.

Geoapify coverage and fields vary. Each search returns at most 20 provider places, so the result list is not an exhaustive hotel inventory.

The saved shortlist stores a snapshot of a provider place ID, name, address, coordinates, timestamp, local simulated nightly rate, and local simulated available-room count in the ignored file `backend/data/assignment2_shortlist.db`. Simulations are stable for a saved provider ID and are not returned by Geoapify. The labeled fixed test data is in [`backend/data/assignment2-shortlist-sample.json`](backend/data/assignment2-shortlist-sample.json); it is not a live Geoapify response.

The assistant sends no database access or LLM key to Vue. FastAPI asks the configured LLM for a single SQL proposal, rejects unsafe or non-`SELECT` output, retrieves at most 20 rows from `shortlisted_places` under SQLite's read-only authorizer, then gives only the question and those retrieved records to the final answer call.

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
OPENROUTER_API_KEY=your-openrouter-key-here
# Optional; the default selects an available free model.
OPENROUTER_MODEL=openrouter/free
```

`.env` is ignored by Git. Never commit it, paste a key into source code, or add it to a report or recording. Geoapify and OpenRouter keys are used only by FastAPI; the Vue browser application never receives them. The assistant returns a clear configuration message until `OPENROUTER_API_KEY` is set and FastAPI is restarted.

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

See the [Part 1 research and mockup](docs/assignment2-part1-research.md), [Part 2 shortlist research](docs/assignment2-part2-research.md), [Part 2 RAG research and mockup](docs/assignment2-part2-rag-research.md), [local simulation design note](docs/local-simulation.md), [the design note](docs/design.md), [selected prompts](prompts/selected-prompts.md), and [the current handoff](handoffs/current.md). The preserved [Assignment 2 Part 1 report](reports/assignment2-part1/report.md) includes the four submitted browser screenshots.
