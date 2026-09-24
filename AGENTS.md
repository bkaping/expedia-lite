# Wayfarer Lite project guidance

- Keep the Vue client in `frontend/` and the FastAPI service in `backend/`.
- Treat `backend/data/*.csv` as starter fixtures. The SQLite database is generated locally and must not be reseeded after its first successful run.
- Make booking changes through API endpoints and the frontend; do not modify the SQLite file by hand.
- Run the backend unit tests and a frontend production build before committing functional changes.
- Keep `docs/design.md`, `prompts/selected-prompts.md`, and `handoffs/current.md` concise and current when the application changes.
