# Assignment 3.3 fictional evaluation

All cases below use only local, fictional records. Routine checks use the fake model in `backend/tests/test_skills.py`; live-model results are listed separately and were limited to two fixed, no-profile prompts on November 2, 2026.

## Fifteen scenarios

| # | Fictional scenario | Expected behavior | Observed / evidence |
| --- | --- | --- | --- |
| 1 | Choose paced breathing | An active local session is created. | Automated session-persistence check passed. |
| 2 | Finish automatic pacing | A 60-second completed session is saved. | Automated completed-session check passed; previous browser check displayed 60 active seconds. |
| 3 | Leave before the first cue | A neutral stopped session with 0 active seconds is saved. | Browser check passed. |
| 4 | Leave after nine active seconds | A neutral stopped session remains reviewable. | Automated stopped-session check passed. |
| 5 | Open Saved history while active | The active session is first saved as stopped; no active record is orphaned. | Browser check passed; November 2 screenshot showed the resulting stopped record. |
| 6 | Use tap-and-hold for 1.2 seconds, then release | Time advances only while held and pauses on release. | Browser check passed: 60 became 59 seconds; ending saved 1 active second. |
| 7 | Use automatic timing, then pause | Active timing stops until continued. | Implemented by the same timer stop/resume path; production build passed. |
| 8 | Save optional profile `Avery` / brief / one short practice | The greeting and cue explanation can adapt from explicit choices. | Automated profile persistence/reset check passed; an earlier isolated browser check showed the changed greeting. |
| 9 | Reset profile | The standard interface returns without removing session history. | Automated reset check passed. |
| 10 | Ask “Does the chatbot read my journal?” | A local factual answer states journal text is not sent to the model. | Automated local-answer check passed. |
| 11 | Ask “What is my saved setup?” | A local answer uses only profile choices and completed-practice count. | Automated setup-context check passed. |
| 12 | Ask for a summary before completing | The model-summary prompt is blocked and no message record is created. | Automated completed-session guard check passed. |
| 13 | Choose a summary after a completed fictional session | The fake model receives only timing, cue/aim choices, and completion count; prompt/reply persist. | Automated context/persistence check passed; display name and journal text were excluded. |
| 14 | Provider/model failure during a summary | A local fallback appears; completed session stays saved and the support panel remains independent. | Automated failing-client fallback check passed. |
| 15 | Save fictional journal text matching the narrow phrase rule | The journal text is not saved and the static support route opens. | Automated journal safety-route check passed. |

## Cross-case behavior checks

| Behavior that must hold | Cases checked | Result |
| --- | --- | --- |
| The fixed 4-in / 6-out skill is not changed by either pacing control or chatbot output. | 2, 6, 7, 10–14 | Passed: controls affect only pacing; the model system prompt forbids skill changes and output validation falls back locally. |
| Crisis support remains browser-local and available when the model path fails. | 1–15, especially 14 and 15 | Passed: the panel is rendered in Vue and makes no FastAPI or model call. |
| Journal content never enters the model-summary context. | 10, 13, 15 | Passed: the fake-model context assertion excludes a saved fictional journal entry; the journal guard prevents limited phrase matches from saving. |

## Mocked versus live model checks

Routine tests used a fake client for deterministic behavior. Two fixed, fictional, no-profile summary prompts were sent through the configured backend model on November 2, 2026:

| Context | Returned model / observed reply | Interpretation |
| --- | --- | --- |
| One completed 60-second session; standard cue; no profile | `dots-studio/dots-3-note-preview:free` — “One paced-breathing session completed with standard cue style for 60 seconds.” | The output stayed within the factual boundary. |
| Two completed 60-second sessions; standard cue; no profile | `nvidia/nemotron-3.5-lightning:free` — “Paced breathing practice: 60 active seconds, 2 sessions completed. Cue style standard. No display name or aim provided.” | The provider/model varied, but the reply stayed factual and within the length/term checks. |

No profile display name, journal text, or free-text user message was sent to the live provider. A proposed live check with profile data was deliberately not run because it would export local profile information unnecessarily.

## Revision, surprising finding, and limit

The original free-text companion was revised into fixed common-question buttons plus one selected model-summary prompt. This lowers typing and disclosure cost while retaining an honest, bounded model contribution and reviewable conversation record.

The surprising finding was that a normal short click on tap-and-hold behaves as a very short hold: it advanced one displayed second during the browser check. The final label therefore explicitly says “Press and hold,” and release is documented as pause.

An untested limitation remains: no peer usability session or real-world use was conducted, and the two live outputs do not establish consistency, usefulness, or clinical effectiveness.
