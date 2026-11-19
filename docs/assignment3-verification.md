# Assignment 3.2 verification record

All scenarios below are fictional. The chatbot accepts no free-text input: seven website questions are local, while one post-completion fixed summary button can use the backend model.

## Automated checks

`python3 -m unittest discover -s backend/tests -v` passed **22 tests** on November 2, 2026. The suite includes the preserved Assignment 2 tests and eleven focused Stillpoint tests:

| Check | Expected / observed result |
| --- | --- |
| Complete session | A 60-second completed session persists and becomes the optional usual-skill shortcut. |
| Stop session | A 9-second stopped session is preserved for review and does not establish a usual skill. |
| Fictional journal save | An explicit fictional journal entry persists locally and is returned newest-first. |
| Journal safety route | Limited potentially urgent wording is not saved and returns the browser to the independent support route. |
| Common website question | “Does the chatbot read my journal?” returns the factual local answer without a model call or stored message. |
| Optional profile | A display name, cue style, and practice aim persist in SQLite, appear in history data, and can be reset to defaults. |
| Chatbot setup answer | “What is my saved setup?” returns only explicit profile choices plus the completed-practice count. |
| Model-summary context | A fake model receives only completed-session timing, explicit profile choices, and completed-practice count; saved journal text is excluded. |
| Model-summary persistence | The fixed selected prompt and returned response are saved in local history. |
| Model-summary failure | A fake provider failure becomes a local fallback; the completed session remains saved. |
| Completion guard | The model-summary request is rejected before completion and creates no message record. |
| Unsafe model output | A directive/therapeutic fake response becomes a local safety fallback. |

`npm run build` from `frontend/` passed on November 2, 2026.

## Browser and API observations

| Scenario | Expected | Observed |
| --- | --- | --- |
| Open Crisis support on the home screen | Static support dialog contains call, text, and chat routes without an API request. | Observed. The browser accessibility tree showed the panel and all three links. |
| Open Coursework chatbot | Persistent button opens fixed question buttons with no free-text field. | Observed on November 2: seven local factual buttons and one distinct “Create a brief practice summary” button appeared. |
| Save a fictional journal entry | The entry saves locally, clears the text area, confirms saving, and appears in the saved-entry list. | Observed on October 29 with “I wrote a fictional coursework journal entry.” |
| Choose breathing, then leave before beginning | No explanation or confirmation; saved `stopped` session with 0 active seconds. | Observed. The finish screen said “You chose to stop. Nothing else is required.” |
| Open Saved history while a practice is active | The current session is first saved as a neutral `stopped` record; no active session is orphaned by navigation. | Observed on October 29. History opened and displayed the newly stopped paced-breathing session. |
| Open Saved history | The stopped session is readable without a score or diagnosis. | Observed. History showed paced breathing with `Stopped`. |
| Complete a timed practice | Six cycles complete at 60 active seconds. | Observed. Finish screen displayed “Active time recorded: 60 seconds.” |
| Choose tap-and-hold pacing | Holding progresses the current 4- or 6-second phase; releasing pauses it. | Observed on October 29: a 1.2-second hold advanced the display from 60 to 59 seconds; release paused it, and ending saved a neutral stopped session with 1 active second. |
| Review selected model summaries | History shows only explicitly selected summary prompts/replies. | Observed on November 2 in an isolated database: two completed sessions and two model-summary prompt/reply pairs appeared in Saved history. |

## Profile and chatbot demonstration evidence

In an isolated local browser check on October 29, the fictional profile `Avery` + `Step-by-step labels` + `Review the 4-in / 6-out pattern` saved successfully. Returning home visibly changed the greeting to “Welcome, Avery,” and displayed both the selected cue explanation and aim. The focused backend test also verifies that **Reset to defaults** removes the profile. For the presentation, open the factual chatbot and choose **What is my saved setup?** to show its limited use of the profile and completed-practice count. After a completed fictional practice, the separate model-summary button may use its timing, cue/aim choices, and count; it never sends a display name, journal entry, or free-text disclosure. No profile-bearing live call was used for the limited live evidence.

## Part 3.2 safety checks

1. **Independent crisis route:** The dialog is rendered in Vue and has no FastAPI/model dependency. It was visible while the running app was in both home and practice states.
2. **User control:** Both the explicit leave route and navigation to Saved history persist a neutral stopped session instead of forcing the 60-second timer or leaving an active record behind.
3. **Chatbot boundary:** Fixed question IDs are the only inputs accepted by the chatbot endpoint. Seven questions are local. The one model question requires a completed session, sends only allowed context from FastAPI, persists its selected prompt/reply, and converts provider/configuration/unsafe-output failure into a local fallback.

## Limits and Part 3.3 evidence

- Grounding is not implemented yet.
- The [Part 3 evaluation](assignment3-evaluation.md) records 15 fictional scenarios, three cross-case behavior checks, two limited live-model results, a revised approach, a surprising finding, and an untested limitation.
- The journal’s narrow phrase check is not risk detection and was not evaluated on real distress content.
- The chatbot is intentionally narrow; the two live outputs do not establish conversational usefulness or clinical usefulness.
- Peer usability testing and the required demonstration/process recordings remain unclaimed until they are recorded.

## Assignment 4.1 preservation — November 19, 2026

The prior Vue implementation is preserved in `frontend/src/stillpoint.js` and reachable at `/stillpoint`; market data is isolated in a new SQLite database. The full backend suite, including the existing Stillpoint tests, passes after integration. The prior README and design are archived as `assignment3-readme.md` and `assignment3-design.md`. No new Stillpoint live-model or crisis-resource validation is claimed for this part.
