# Current handoff — Wayfarer Lite

## What works

- Vue search displays matching hotel stays in a labeled table and handles no matches.
- FastAPI exposes search plus booking create, history read, cancellation update, and deletion endpoints.
- SQLite seeds once from the CSV fixtures and preserves changes across browser refreshes and backend restarts.
- Controller tests cover joined search, one-time seeding, create, cancel, delete, and reopening the database.

## Checked

- `python3 -m unittest discover -s backend/tests -v`
- `npm run build` from `frontend/`
- Browser check against an isolated local database: matching search, no-results feedback, booking creation, cancellation that retained history, and persistence after refresh.
- API check against an isolated local database: search returned joined hotel/stay data; POST, PATCH, and DELETE returned successful responses.

## Remaining limitations and next task

The included CSV records are clearly marked demo fixtures because the course-supplied files were not in the workspace. Replace them with the supplied rows before final submission, then repeat the browser checks using those data, test the visible **Delete test booking** action, and update `report.md` with screenshots plus the real repository URL and commits. This repository has no Git history or remote yet.
