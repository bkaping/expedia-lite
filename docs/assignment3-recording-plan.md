# Assignment 3.3 recording plan

Use fictional records only. Do not show `.env`, API keys, or personal data. The two short sections below satisfy the required finished demo and failure-investigation structure when recorded.

## Section A — finished application demonstration (about 3 minutes)

1. Start on **Practice**. State: “Stillpoint is a localhost-only coursework prototype for fictional scenarios, not therapy, diagnosis, monitoring, or crisis care.”
2. Open **My profile**. Set the fictional choices `Avery`, `Step-by-step labels`, and `Review the 4-in / 6-out pattern`; save. Return to Practice and show the greeting/cue adaptation. Reset at the end to demonstrate user correction.
3. Choose paced breathing. Show both **Automatic visual timing** and **Tap-and-hold pacing**. Explain that both use exactly six 4-in / 6-out cycles and that releasing tap-and-hold pauses rather than changing a skill step.
4. Show **Crisis support** while on the practice screen. State that it is already in the browser and independent of FastAPI/model behavior.
5. Complete one fictional practice or show a pre-seeded 60-second completed record. Open **Coursework chatbot**. Select a local factual question, then **Create a brief practice summary**. Explain that there is no free-text input, and only the selected summary prompt/reply is saved.
6. Open **Saved history** and show sessions plus the selected model-summary exchange. Open **Journal** and state that journal text remains separate and never enters the model prompt.

## Section B — failure investigation and code explanation (about 2 minutes)

1. Run the backend with no `OPENROUTER_API_KEY` in a temporary environment, then choose the fixed practice-summary prompt after a completed fictional session.
2. Show the local fallback message and Saved history. State that the completed session remains intact and Crisis support did not depend on the request.
3. Open `backend/app/skills_companion.py`. Explain `_model_summary`: it accepts only a completed-session ID, builds context from session timing plus cue/aim choices and count, omits display name and journal text, validates output, and saves a local fallback after a configuration/provider/unsafe-output failure.
4. Open `backend/tests/test_skills.py`. Explain the fake-client checks for allowed context, persistence, completion gating, provider failure, and unsafe output.
5. Close with the evaluation limitation: two live outputs varied by provider/model, but neither establishes usefulness or clinical effectiveness.
