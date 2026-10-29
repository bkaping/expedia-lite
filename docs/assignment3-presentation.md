# Assignment 3 presentation walkthrough

All examples are fictional coursework scenarios. Do not describe Stillpoint as therapy, diagnosis, monitoring, crisis care, or a tool to rely on while distressed.

## 1. User state and interface adaptation

1. Open **My profile**. Explain that every field is optional and editable: a display name, a cue style, and a practice aim.
2. Set the fictional profile to `Avery`, `Step-by-step labels`, and `Review the 4-in / 6-out pattern`; save it.
3. Return to Practice. Show the personalized greeting and the changed cue explanation. If there is a completed session, show the optional repeat shortcut.
4. Explain the assumption: these are user-selected interface choices, not a clinical check-in, sensor, or distress detector. Press **Reset to defaults** to demonstrate correction/override.

## 2. Skill walkthrough and research grounding

1. Choose **Paced breathing (4–6)** and show the preparation screen.
2. Explain the fixed skill: six cycles of four-second inhale and six-second exhale, measured as 60 active seconds. The chatbot cannot alter these steps.
3. Start the practice; show pause and end controls. End early if time is limited, explaining that stopping is consequence-free and records a neutral stopped session.
4. Open **Crisis support**. Explain it is a static browser route, independent of FastAPI and the chatbot.
5. Tie the design to the documented findings: short attention-friendly duration, one atomic activity, low-stimulus presentation, no required disclosure, user control, and persistent support access.

## 3. Persona, interaction choices, and accessibility

1. Return to **My profile** and explain exactly what is saved locally in SQLite: the optional display name, cue style, practice aim, update time, sessions, and optional fictional chatbot messages.
2. Explain how it updates: **Save profile** overwrites choices; **Reset to defaults** removes them. The saved history can offer—but never force—the latest completed skill as a repeat shortcut.
3. Demonstrate keyboard use with Tab/Enter, visible focus outlines, native form controls, clear labels, and the browser's reduced-motion setting, which removes the breathing animation while retaining text/count cues.
4. Explain why this reduces effort: defaults work with no setup; choices are structured rather than emotionally demanding; a message is never required.

## 4. Chatbot tone and limits

1. Complete the fictional practice, then send an ordinary fictional message such as: `I followed the fictional count.`
2. Show the short response and label it a **coursework chatbot**. Explain it receives only the fictional message, explicit profile choices, and completed-practice count.
3. Describe the tone: brief, neutral, nonjudgmental, and choice-preserving. It does not claim understanding, diagnosis, therapeutic authority, or medical expertise.
4. Describe the hard limits: it runs only after completion; cannot change the breathing skill, timer, exits, records, or support panel; output over 120 characters or containing prohibited therapeutic/directive terms becomes a local fixed fallback. Limited potential-crisis phrases are neither saved nor sent to the model; this is not a distress detector.

## Close

Show Saved history and restate that this is a localhost-only fictional coursework prototype. State one limitation honestly: the profile and chatbot are intentionally narrow and do not establish clinical usefulness or reliability.
