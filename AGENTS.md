# Wayfarer Lite project guidance

- Keep the Vue client in `frontend/` and the FastAPI service in `backend/`.
- MVC responsibilities: Vue owns ZIP input, status presentation, and list/map selection; FastAPI is the credential-safe request boundary; `GeoapifyHotelController` validates provider responses and returns live-place models. The browser must never receive the Geoapify key.
- Preserve provider truth: use only provider names, addresses, place IDs, and coordinates. Label missing fields honestly; never invent price, rating, availability, or booking data.
- Store credentials only in root `.env`. Keep `.env` ignored and commit only `.env.example`.
- Follow CHECK → TAKE ACTION → VERIFY before a new dependency: inspect the existing environment, explain the exact installation and wait for student approval, then install and verify with focused checks and a build.
- Keep the visible map attribution. List cards and markers must share the same selected place and work with a keyboard.
- Run backend unit tests and a frontend production build before committing functional changes.
- Keep `docs/design.md`, `docs/assignment2-part1-research.md`, `prompts/selected-prompts.md`, and `handoffs/current.md` concise and current when the application changes.
