# Assignment 3.2 verification record

All scenarios below are fictional. The current chatbot uses local fixed answers and has no language-model path or free-text input.

## Automated checks

`python3 -m unittest discover -s backend/tests -v` passed **18 tests** on October 29, 2026. The suite includes the preserved Assignment 2 tests and seven focused Stillpoint tests:

| Check | Expected / observed result |
| --- | --- |
| Complete session | A 60-second completed session persists and becomes the optional usual-skill shortcut. |
| Stop session | A 9-second stopped session is preserved for review and does not establish a usual skill. |
| Fictional journal save | An explicit fictional journal entry persists locally and is returned newest-first. |
| Journal safety route | Limited potentially urgent wording is not saved and returns the browser to the independent support route. |
| Common website question | “Does the chatbot read my journal?” returns the factual local answer. |
| Optional profile | A display name, cue style, and practice aim persist in SQLite, appear in history data, and can be reset to defaults. |
| Chatbot setup answer | “What is my saved setup?” returns only explicit profile choices plus the completed-practice count. |

`npm run build` from `frontend/` passed on October 29, 2026.

## Browser and API observations

| Scenario | Expected | Observed |
| --- | --- | --- |
| Open Crisis support on the home screen | Static support dialog contains call, text, and chat routes without an API request. | Observed. The browser accessibility tree showed the panel and all three links. |
| Open Coursework chatbot | Persistent button opens a factual question panel with no free-text field. | Observed on October 29: seven question buttons appeared, and “What is my saved setup?” returned only no-profile/no-completed-practice facts in an isolated temporary database. |
| Save a fictional journal entry | The entry saves locally, clears the text area, confirms saving, and appears in the saved-entry list. | Observed on October 29 with “I wrote a fictional coursework journal entry.” |
| Choose breathing, then leave before beginning | No explanation or confirmation; saved `stopped` session with 0 active seconds. | Observed. The finish screen said “You chose to stop. Nothing else is required.” |
| Open Saved history while a practice is active | The current session is first saved as a neutral `stopped` record; no active session is orphaned by navigation. | Observed on October 29. History opened and displayed the newly stopped paced-breathing session. |
| Open Saved history | The stopped session is readable without a score or diagnosis. | Observed. History showed paced breathing with `Stopped`. |
| Complete a timed practice | Six cycles complete at 60 active seconds. | Observed. Finish screen displayed “Active time recorded: 60 seconds.” |
| Choose tap-and-hold pacing | Holding progresses the current 4- or 6-second phase; releasing pauses it. | Observed on October 29: a 1.2-second hold advanced the display from 60 to 59 seconds; release paused it, and ending saved a neutral stopped session with 1 active second. |

## Profile and chatbot demonstration evidence

In an isolated local browser check on October 29, the fictional profile `Avery` + `Step-by-step labels` + `Review the 4-in / 6-out pattern` saved successfully. Returning home visibly changed the greeting to “Welcome, Avery,” and displayed both the selected cue explanation and aim. The focused backend test also verifies that **Reset to defaults** removes the profile. For the presentation, open the factual chatbot and choose **What is my saved setup?** to show its limited use of the profile and completed-practice count. No disclosure is accepted or required.

## Part 3.2 safety checks

1. **Independent crisis route:** The dialog is rendered in Vue and has no FastAPI/model dependency. It was visible while the running app was in both home and practice states.
2. **User control:** Both the explicit leave route and navigation to Saved history persist a neutral stopped session instead of forcing the 60-second timer or leaving an active record behind.
3. **Chatbot boundary:** Fixed question IDs are the only inputs accepted by the chatbot endpoint. It accepts no free-text message, stores no chatbot prompt or answer, and makes no model request.

## Limits and Part 3.3 plan

- Grounding is not implemented yet.
- The 15 fictional scenarios, three cross-case behavior checks, peer/mock testing, and process screencast belong to Part 3.3.
- The journal’s narrow phrase check is not risk detection and was not evaluated on real distress content.
- The fixed chatbot is intentionally narrow; it does not establish conversational usefulness or clinical usefulness.
