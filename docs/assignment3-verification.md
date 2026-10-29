# Assignment 3.2 verification record

All scenarios below are fictional. Automated checks use a fake model; the one browser model check used a fictional note only.

## Automated checks

`python3 -m unittest discover -s backend/tests -v` passed **16 tests** on October 29, 2026. The suite includes the preserved Assignment 2 tests and five Part 3.2 tests:

| Check | Expected / observed result |
| --- | --- |
| Complete session | A 60-second completed session persists and becomes the optional usual-skill shortcut. |
| Stop session | A 9-second stopped session is preserved for review and does not establish a usual skill. |
| Ordinary fictional note | Fake model receives the completed skill context; user note and bounded reply persist. |
| Potential-crisis phrase | Fake model receives zero calls; only a generic system record is stored, not the phrase. |
| Unsafe model reply | “You should seek therapy” is replaced with the local safety fallback. |

`npm run build` from `frontend/` passed on October 29, 2026.

## Browser and API observations

| Scenario | Expected | Observed |
| --- | --- | --- |
| Open Crisis support on the home screen | Static support dialog contains call, text, and chat routes without an API request. | Observed. The browser accessibility tree showed the panel and all three links. |
| Choose breathing, then leave before beginning | No explanation or confirmation; saved `stopped` session with 0 active seconds. | Observed. The finish screen said “You chose to stop. Nothing else is required.” |
| Open Saved history while a practice is active | The current session is first saved as a neutral `stopped` record; no active session is orphaned by navigation. | Observed on October 29. History opened and displayed the newly stopped paced-breathing session. |
| Open Saved history | The stopped session is readable without a score or diagnosis. | Observed. History showed paced breathing with `Stopped`. |
| Complete a timed practice | Six cycles complete at 60 active seconds. | Observed. Finish screen displayed “Active time recorded: 60 seconds.” |
| Send an ordinary fictional note | Optional model acknowledgment returns; practice remains saved. | Observed. The model returned `Acknowledged.` for “I followed the fictional count.” |
| Run a key-disabled local companion API | No provider call; a clear configuration failure response is returned. | Rechecked on October 29. `POST /api/conversations` returned HTTP 503 with `companion_not_configured`. |

## Part 3.2 safety checks

1. **Independent crisis route:** The dialog is rendered in Vue and has no FastAPI/model dependency. It was visible while the running app was in both home and practice states.
2. **User control:** Both the explicit leave route and navigation to Saved history persist a neutral stopped session instead of forcing the 60-second timer or leaving an active record behind.
3. **Model boundary:** The fake-client tests prove that potential-crisis content is not sent to the model and that out-of-role output becomes a local fallback. The live browser check used only a fictional ordinary note.

## Limits and Part 3.3 plan

- Grounding is not implemented yet.
- The 15 fictional scenarios, three cross-case behavior checks, peer/mock testing, and process screencast belong to Part 3.3.
- The narrow phrase check is not risk detection and was not evaluated on real distress content.
- The browser model test shows one response only; it does not establish consistency or clinical usefulness.
