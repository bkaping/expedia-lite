# Assignment 3 presentation walkthrough

All examples are fictional coursework scenarios. Do not describe Stillpoint as therapy, diagnosis, monitoring, crisis care, or a tool to rely on while distressed.

## 1. User state and interface adaptation

1. Open **My profile**. Explain that every field is optional and editable: a display name, a cue style, and a practice aim.
2. Set the fictional profile to `Avery`, `Step-by-step labels`, and `Review the 4-in / 6-out pattern`; save it.
3. Return to Practice. Show the personalized greeting and the changed cue explanation. If there is a completed session, show the optional repeat shortcut.
4. Explain the assumption: these are user-selected interface choices, not a clinical check-in, sensor, or distress detector. Press **Reset to defaults** to demonstrate correction/override.

## 2. Skill walkthrough and research grounding

1. Choose **Paced breathing (4–6)** and show the preparation screen.
2. Explain the fixed skill: six cycles of four-second inhale and six-second exhale, measured as 60 active seconds. Choose **Automatic visual timing**, then show the visual cue and pause/end controls.
3. Return to preparation and choose **Tap-and-hold pacing**. Explain that holding counts the current inhale or exhale and releasing pauses it; each phase still ends at four or six active seconds, so the interaction choice never changes the skill steps.
4. End early if time is limited, explaining that stopping is consequence-free and records a neutral stopped session.
5. Open **Crisis support**. Explain it is a static browser route, independent of FastAPI and the chatbot.
6. Tie the design to the documented findings: short attention-friendly duration, one atomic activity, low-stimulus presentation, no required disclosure, user control, and persistent support access.

## 3. Persona, interaction choices, and accessibility

1. Return to **My profile** and explain exactly what is saved locally in SQLite: the optional display name, cue style, practice aim, update time, sessions, and separate fictional journal entries. Open **Journal** to show that entries are never sent to a model.
2. Explain how it updates: **Save profile** overwrites choices; **Reset to defaults** removes them. The saved history can offer—but never force—the latest completed skill as a repeat shortcut.
3. Demonstrate keyboard use with Tab/Enter, visible focus outlines, native form controls, clear labels, and the browser's reduced-motion setting, which removes the breathing animation while retaining text/count cues.
4. Explain why this reduces effort: defaults work with no setup; automatic and tap-and-hold controls let the person choose how to pace the same skill; no chatbot message or journal entry is required.

## 4. Chatbot tone and limits

1. Point out the persistent **Coursework chatbot** button beside Crisis support. Open it and choose **What information is saved?** to show a factual local answer.
2. Then choose **What is my saved setup?** after saving the fictional profile. Explain that it reads only the optional profile choices and the completed-practice count.
3. Describe the tone: short, factual, neutral, and nonjudgmental. It does not claim understanding, diagnosis, therapeutic authority, or medical expertise.
4. Describe the hard limits: it accepts no free-text messages, stores no chatbot messages, and makes no language-model request. It cannot change the breathing skill, timer, exits, records, or support panel. It identifies itself honestly as a coursework prototype, not therapy or crisis care.

## Close

Show Saved history and restate that this is a localhost-only fictional coursework prototype. State one limitation honestly: the profile and chatbot are intentionally narrow and do not establish clinical usefulness or reliability.
