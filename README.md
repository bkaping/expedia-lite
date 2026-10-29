# Stillpoint — Assignment 3.2 Mental Health Skills Prototype

Stillpoint is a localhost-only coursework prototype for **fictional scenarios only**. It is not therapy, diagnosis, crisis care, monitoring, or a service anyone should rely on during distress.

## Implemented Part 3.2 scope

- One complete study-provided skill: paced breathing, six 4-second inhale / 6-second exhale cycles (60 active seconds).
- A clear preparation screen, pause control, and consequence-free leave route; stopped sessions are saved with their active time.
- A browser-local **Crisis support** panel visible on every screen. It contains current U.S. 988 call, text, and chat links and remains available if FastAPI or the model fails.
- SQLite persistence for recent session records and explicit optional fictional companion notes.
- A backend-only, optional model acknowledgment after a completed session. It cannot set skill steps, timing, exits, persistence, or crisis access; potentially urgent text is not sent to the model or stored verbatim.
- A saved-history view plus an optional “use this practice again” shortcut after a previous completion. No setup or automatic routing occurs.

5–4–3–2–1 grounding remains a documented design direction, not an implemented Part 3.2 claim.

## Run locally

Requirements: Python 3.11+ and Node.js 20+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the displayed Vite URL. The development server proxies `/api` to FastAPI, so the browser uses same-origin requests in local development.

The skill, SQLite history, and crisis panel work without an API key. The optional model companion needs `OPENROUTER_API_KEY`: copy `.env.example` to root `.env`, add the key, and restart FastAPI. Keep `.env` ignored; the browser never receives this key.

## Verification

```bash
python3 -m unittest discover -s backend/tests -v
cd frontend && npm run build
```

The current checkout was rechecked on October 29, 2026: 16 tests passed and the production build passed. Browser evidence, model boundaries, timing, failure behavior, and remaining limitations are documented in [the verification record](docs/assignment3-verification.md).

## Documentation

- [Part 3.2 design and safety decisions](docs/design.md)
- [Part 3.2 submission report](report.md)
- [Verification record](docs/assignment3-verification.md)
- [Selected prompts](prompts/selected-prompts.md)
- [Evidence log](docs/evidence-log.md)
- [AI-use disclosure](AI-USE.md)
- [Current handoff](handoffs/current.md)
