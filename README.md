# Stillpoint — Assignment 3 Mental Health Skills Prototype

Stillpoint is a localhost-only coursework prototype for **fictional scenarios only**. It is not therapy, diagnosis, crisis care, monitoring, or a service anyone should rely on during distress.

## Implemented Part 3.2 scope

- One complete study-provided skill: paced breathing, six 4-second inhale / 6-second exhale cycles (60 active seconds).
- A clear preparation screen with two controls for the same fixed sequence: automatic visual timing or tap-and-hold pacing. Both support a consequence-free leave route; stopped sessions are saved with their active time.
- A browser-local **Crisis support** panel visible on every screen. It contains current U.S. 988 call, text, and chat links and remains available if FastAPI fails.
- SQLite persistence for recent session records, an optional local profile, optional fictional journal entries, and selected model-summary exchanges.
- An optional **Journal** page saves up to 500-character fictional entries locally in SQLite. Journal text is never sent to the chatbot or model; limited potentially urgent wording is not saved.
- An optional profile holds only a display name, cue-style choice, and practice-aim choice. It changes the greeting and cue explanation; it can be edited or reset without completing a practice.
- A persistent **Coursework chatbot** control opens seven fixed factual questions plus one optional fixed model-summary prompt after a completed fictional practice. It accepts no free-text messages. The model receives only session timing, cue/aim choices, and completed-practice count; selected prompt/reply pairs are saved locally for review.
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

The skill, SQLite history, support panel, and local factual questions work without an API key. `OPENROUTER_API_KEY` enables only the optional fixed practice-summary prompt; the browser never receives the key.

## Verification

```bash
python3 -m unittest discover -s backend/tests -v
cd frontend && npm run build
```

The current checkout is verified with backend unit tests, a frontend production build, fictional browser checks, and two limited live-model calls. Browser evidence, timing, interaction controls, and remaining limitations are documented in [the verification record](docs/assignment3-verification.md) and [Part 3 evaluation](docs/assignment3-evaluation.md).

## Documentation

- [Part 3.2 design and safety decisions](docs/design.md)
- [Part 3 presentation walkthrough](docs/assignment3-presentation.md)
- [Part 3.2 submission report](report.md)
- [Verification record](docs/assignment3-verification.md)
- [Part 3 fictional evaluation](docs/assignment3-evaluation.md)
- [Part 3 recording plan](docs/assignment3-recording-plan.md)
- [Selected prompts](prompts/selected-prompts.md)
- [Evidence log](docs/evidence-log.md)
- [AI-use disclosure](AI-USE.md)
- [Current handoff](handoffs/current.md)
