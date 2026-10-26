# Assignment 3.1 evidence log

This record documents the Part 3.1 design milestone only. It contains no real-person disclosures, participant information, credentials, live model calls, or claims that the design is already implemented.

| Date | Evidence / action | Design decision |
| --- | --- | --- |
| 2026-10-26 | Reviewed the assignment’s R1–R4 and D1–D6 study summary. | Designed two low-demand skills, one planned for 60 active seconds and one planned for 45–75 seconds; neither exceeds the 90-second exercise limit. |
| 2026-10-26 | Sketched the home, active paced-breathing, and history states. | Made support access and leave/end controls visible in every relevant state; no explanation is requested to leave. |
| 2026-10-26 | Considered typed grounding answers. | Rejected required text entry because it would add effort and create unnecessary sensitive records; the canonical 5–4–3–2–1 sequence remains visible. |
| 2026-10-26 | Considered automatic last-skill routing. | Rejected it in favor of an optional repeat shortcut so both skills stay available and the person keeps control. |
| 2026-10-26 | Scoped the optional model contribution. | Limited it to a short, post-completion acknowledgment of an explicit fictional note; the app retains control of skill steps, timer, exits, records, and crisis route. |

## Planned verification for later parts

Part 3.2 will measure the running paced-breathing exercise from the first cue through the final planned step, separately note setup time, test a voluntary leave path, inspect SQLite records, and show the browser-local support route after a model/API failure. Part 3.3 will record the required fictional scenarios, behavior checks, and comparison of mocked versus limited live-model behavior.
