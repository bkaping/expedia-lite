# Assignment 2 Part 2 — live RAG verification

Verification date: October 6, 2026. Provider: OpenRouter free router. The provider selected `nvidia/nemotron-3-super-120b-a12b:free` for this observed run; free-model availability can change.

## Observed workflow

| Stage | Expected | Observed |
| --- | --- | --- |
| Traveler question | A saved-hotel question reaches the backend. | “Which saved hotel has the lowest simulated nightly rate, and how many simulated rooms are available?” |
| LLM SQL proposal | One allowed read-only query against `shortlisted_places`. | `SELECT name, simulated_nightly_rate_usd, simulated_available_rooms FROM shortlisted_places WHERE saved_at IS NOT NULL ORDER BY simulated_nightly_rate_usd ASC LIMIT 1` |
| Backend retrieval | SQLite returns only the records produced by the validated query. | Fairfield Inn & Suites; `simulated_nightly_rate_usd: 156.49`; `simulated_available_rooms: 5`. |
| Grounded answer | The second LLM call uses the original question and retrieved record, without claiming provider inventory. | The answer identified Fairfield Inn & Suites and explicitly described `$156.49` and `5` rooms as local simulations. |

## Safety checks

- Planner output is limited to one direct `SELECT` from `shortlisted_places`, with a maximum of 20 rows.
- The backend rejects write operations, comments, joins, other tables, and oversized limits before running SQLite.
- SQLite's authorization callback permits only reads from `shortlisted_places` during retrieval.
- The Vue browser receives only the question, visible proposed SQL, records, answer, and model name. It never receives the OpenRouter key.
