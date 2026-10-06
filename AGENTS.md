# Wayfarer Lite project guidance

- Keep the Vue client in `frontend/` and the FastAPI service in `backend/`.
- MVC responsibilities: Vue owns ZIP input, status presentation, list/map selection, and shortlist controls; FastAPI is the credential-safe request boundary; `GeoapifyHotelController` validates provider responses and returns live-place models; `ShortlistController` persists saved snapshots in SQLite. The browser must never receive the Geoapify key.
- RAG responsibilities: Vue sends a user question and displays the complete grounded workflow; FastAPI alone calls the LLM twice, validates the LLM's SQL proposal, executes the local retrieval, and returns the question, proposed SQL, retrieved records, answer, and model name. The browser must never receive an LLM credential.
- Preserve provider truth: use only provider names, addresses, place IDs, and coordinates as provider data. Label missing fields honestly. Locally generated rate and availability simulations are allowed only after a hotel is saved and must be visibly labeled as simulations, never as provider prices, real availability, or bookings.
- Store credentials only in root `.env`. Keep `.env` ignored and commit only `.env.example`.
- Keep the generated shortlist database ignored. Use the labeled JSON fixture for repeatable tests, never as though it were live provider data. Use provider place ID as the SQLite uniqueness key and preserve the first saved snapshot when a duplicate save is requested.
- When extending a saved snapshot, perform a compatible SQLite migration so existing saved places remain readable. Generate local simulations in the backend and persist them with the saved place.
- For hotel-assistant retrieval, accept only one validated `SELECT` query from `shortlisted_places`, cap results at 20, and use SQLite's authorizer as a second read-only enforcement layer. Send the original question and exact retrieved records to the answer-generation call; never allow model output to write to SQLite.
- Follow CHECK → TAKE ACTION → VERIFY before a new dependency: inspect the existing environment, explain the exact installation and wait for student approval, then install and verify with focused checks and a build.
- Keep the visible map attribution. List cards and markers must share the same selected place and work with a keyboard.
- Run backend unit tests and a frontend production build before committing functional changes.
- Keep `docs/design.md`, all Assignment 2 research notes, `prompts/selected-prompts.md`, and `handoffs/current.md` concise and current when the application changes.
