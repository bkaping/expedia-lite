# Wayfarer Lite project guidance

- Keep the Vue client in `frontend/` and the FastAPI service in `backend/`.
- MVC responsibilities: Vue owns ZIP input, status presentation, list/map selection, and shortlist controls; FastAPI is the credential-safe request boundary; `GeoapifyHotelController` validates provider responses and returns live-place models; `ShortlistController` persists saved snapshots in SQLite. The browser must never receive the Geoapify key.
- Preserve provider truth: use only provider names, addresses, place IDs, and coordinates. Label missing fields honestly; never invent price, rating, availability, or booking data.
- Store credentials only in root `.env`. Keep `.env` ignored and commit only `.env.example`.
- Keep the generated shortlist database ignored. Use the labeled JSON fixture for repeatable tests, never as though it were live provider data. Use provider place ID as the SQLite uniqueness key and preserve the first saved snapshot when a duplicate save is requested.
- Follow CHECK → TAKE ACTION → VERIFY before a new dependency: inspect the existing environment, explain the exact installation and wait for student approval, then install and verify with focused checks and a build.
- Keep the visible map attribution. List cards and markers must share the same selected place and work with a keyboard.
- Run backend unit tests and a frontend production build before committing functional changes.
- Keep `docs/design.md`, both Assignment 2 research notes, `prompts/selected-prompts.md`, and `handoffs/current.md` concise and current when the application changes.
