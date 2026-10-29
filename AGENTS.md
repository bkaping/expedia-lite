# Stillpoint project guidance

- Keep the Vue client in `frontend/` and the FastAPI service in `backend/`. Vue owns the skill flow, pacing cue, exits, visible history, and static crisis panel. FastAPI owns SQLite and all optional LLM calls. The browser must never receive an LLM key.
- This is a coursework prototype for fictional scenarios only. Never describe it as therapy, diagnosis, monitoring, crisis care, or something a person should rely on while distressed.
- Keep the canonical skill steps intact. Part 3.2 implements paced breathing (inhale 4 / exhale 6); 5–4–3–2–1 grounding remains documented as planned. Do not let generated output add, reorder, or replace a skill step.
- Keep crisis support persistently visible and functional in the browser even if FastAPI or the LLM fails. Any input screening is limited, documented, and must never be represented as a distress detector.
- Minimize emotional and data cost: do not require a disclosure to finish a skill. Store only the documented session fields and explicit optional fictional notes. Do not store or transmit detected potential-crisis content.
- Personalization may offer the latest completed skill as a shortcut but must not auto-route someone, hide the other choices, or require a preferences setup flow.
- Store credentials only in root `.env`; keep it ignored and commit only `.env.example`. Keep generated SQLite databases ignored.
- Follow CHECK → TAKE ACTION → VERIFY before adding a dependency: inspect the existing environment, explain the exact installation and wait for student approval, then install and verify with focused checks and a build.
- Preserve keyboard usability and the `prefers-reduced-motion` alternative for the visual breathing cue.
- Run backend unit tests and a frontend production build before committing functional changes.
- Keep `README.md`, `docs/design.md`, `docs/assignment3-verification.md`, `prompts/selected-prompts.md`, and `handoffs/current.md` concise and current when the application changes.
