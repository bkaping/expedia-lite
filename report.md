# Wayfarer Lite — Assignment 2 Part 2

## Project access and assessed commit

- Repository: [https://github.com/bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
- Assessed implementation commit: [124df06](https://github.com/bkaping/expedia-lite/commit/124df06)
- Startup and local configuration: [README.md](README.md). Root `.env` contains `GEOAPIFY_API_KEY` and `OPENROUTER_API_KEY` locally only; it is ignored by Git and neither secret appears in the browser, repository, screenshots, or video.
- Fixed local-storage fixture: [`backend/data/assignment2-shortlist-sample.json`](backend/data/assignment2-shortlist-sample.json). It is fixed test data, not a live provider response.

## Part 1 foundation and local storage

Part 1 resolves an exact five-digit U.S. ZIP through Geoapify and shows nearby provider hotel places in a synchronized Leaflet map and list. The preserved [Part 1 report](reports/assignment2-part1/report.md) includes its live-results, marker-selection, list-selection, and invalid-ZIP screenshots.

The local-storage foundation saves a provider-place snapshot in SQLite: provider ID, name, address, coordinates, saved timestamp, local simulated nightly rate, and local simulated available-room count. The rate and availability are always identified as local simulations—not Geoapify prices, live room inventory, or bookings. Duplicate provider IDs retain the original saved snapshot.

## Research and early mockup

- [Part 2 shortlist research](docs/assignment2-part2-research.md)
- [RAG research and early mockup](docs/assignment2-part2-rag-research.md)
- [Design note](docs/design.md)

![Early grounded-assistant mockup](docs/assignment2-part2-rag-mockup.svg)

The research selected OpenRouter's backend HTTP API and free-model router because the account key stays server-side and free model availability can change. SQLite is sufficient for retrieval because the saved-hotel collection is small; no vector database is used.

## Required grounded workflow

1. Vue sends the traveler’s saved-hotel question to `POST /api/hotel-assistant`.
2. FastAPI gives the LLM the `shortlisted_places` schema and strict query rules. The LLM returns a visible JSON SQL proposal.
3. FastAPI validates the proposal: exactly one comment-free `SELECT`, only `shortlisted_places`, no joins or write operations, and a maximum of 20 rows. SQLite's authorization callback independently permits only reads from that table.
4. FastAPI executes the validated local query, then sends the original question and exact retrieved records to the LLM a second time.
5. Vue displays the question, proposed SQL, retrieved records, grounded answer, and provider-reported model name.

The browser never receives the OpenRouter credential or direct database access.

## Live verification record

Verification date: October 6, 2026. The free router selected `nvidia/nemotron-3-super-120b-a12b:free` for this observed run; model availability can vary.

| Action | Expected result | Observed result |
| --- | --- | --- |
| Ask “Which saved hotel has the lowest simulated nightly rate, and how many simulated rooms are available?” | The LLM proposes a read-only query over saved hotels. | Proposed: `SELECT name, simulated_nightly_rate_usd, simulated_available_rooms FROM shortlisted_places WHERE saved_at IS NOT NULL ORDER BY simulated_nightly_rate_usd ASC LIMIT 1` |
| Validate and execute the proposal | Backend permits one safe local read and returns matching records only. | Retrieved: Fairfield Inn & Suites with `simulated_nightly_rate_usd: 156.49` and `simulated_available_rooms: 5`. |
| Send the original question plus retrieved record to the LLM | Answer is actionable and grounded, with simulations clearly labeled. | The answer identified Fairfield Inn & Suites as the lowest saved option and explicitly described `$156.49` and `5` rooms as local simulations. |
| Test unsafe plans | Writes, other tables, and excessive result limits are rejected before execution. | Focused tests reject `DELETE`, `sqlite_master`, and `LIMIT 99` proposals. |
| Test data persistence | A saved provider record and its simulations survive reopening SQLite. | Focused tests cover duplicate prevention, legacy-table migration, persistence, and removal. |
| Run automated checks | Backend tests and frontend production build pass. | `python3 -m unittest discover -s backend/tests -v`: 11 passing tests. `npm run build` from `frontend/`: passed. |

The detailed [live RAG verification record](docs/assignment2-part2-rag-verification.md) preserves the question, SQL, records, answer behavior, and safety checks.

## Recorded demo video (under three minutes)

Pending recording and accessible link. The video will show: a saved hotel with local simulated rate/availability; the question above; the visible proposed SQL; the retrieved record; the grounded answer and model; and a local database check or refresh that confirms the saved values are read from SQLite. It will not show API keys.

## AI disclosure and evidence log

- OpenAI Codex (GPT-5) assisted with implementation, testing, documentation, and the verification workflow.
- [Selected prompts](prompts/selected-prompts.md) record the local-simulation and revised grounded-RAG implementation requests.
- [Current handoff](handoffs/current.md) records the live October 6 result and remaining student-recorded evidence.
- OpenRouter integration follows the [official Quickstart](https://openrouter.ai/docs/quickstart); model selection uses the [free model collection](https://openrouter.ai/collections/free-models). SQLite's additional read-only protection uses [Python's authorization callback](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.set_authorizer).

## Remaining submission step

Record the required local browser demonstration, upload the video somewhere the instructor can access, paste the link into the demo section above, then upload this root `report.md` on the Assignment 2 Part 2 submission page.
