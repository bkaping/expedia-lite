# Stillpoint — Assignment 3.1 Research and Design

## Submission checkpoint and review links

- Repository: [bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
- **Submitted Part 3.1 design checkpoint:** [`6de604fc2d7656fc83706b26bd58e9cfff3aecec`](https://github.com/bkaping/expedia-lite/commit/6de604fc2d7656fc83706b26bd58e9cfff3aecec) — `docs: add assignment 3 part 1 design package`
- **Design note:** [Assignment 3.1 research and interface design](https://github.com/bkaping/expedia-lite/blob/6de604f/docs/assignment3-part1-design.md)
- **Interface concept:** [open the SVG mockup](https://github.com/bkaping/expedia-lite/blob/6de604f/docs/assignment3-part1-interface.svg)
- **Design evidence log:** [Assignment 3.1 evidence](https://github.com/bkaping/expedia-lite/blob/6de604f/docs/assignment3-part1-evidence.md)
- **Selected prompts and decisions:** [curated Part 3.1 record](https://github.com/bkaping/expedia-lite/blob/6de604f/prompts/assignment3-part1-selected-prompts.md)
- **AI-use disclosure:** [Part 3.1 disclosure](https://github.com/bkaping/expedia-lite/blob/6de604f/reports/assignment3-part1/AI-USE.md)

All review links are pinned to the checkpoint above rather than to a moving branch. The report is submitted separately to the course site; the linked commit contains every referenced design artifact.

## Proposed application

Stillpoint is a **localhost-only coursework prototype for fictional scenarios**. It is not therapy, diagnosis, monitoring, crisis care, or a service that someone should rely on while distressed.

The design supports two study-provided skills:

1. **Paced breathing (4–6):** six four-second inhales and six-second exhales. The planned active exercise takes **60 seconds**, measured from the first “Breathe in” cue to the final exhale; setup is separately estimated at 10–15 seconds.
2. **5–4–3–2–1 sensory grounding:** the canonical five-seen, four-felt, three-heard, two-smelled, one-tasted sequence. It is planned for **45–75 seconds** with no required typed response.

Both are below the assignment’s 90-second exercise limit. A person can pause or leave before and during a skill, without explanation. The design does not infer distress, automatically route a person into a skill, or require a preference setup.

## Interface concept

![Stillpoint interface concept: a skill-choice screen, paced-breathing screen, and recent-history screen. Each keeps Crisis support visible.](https://raw.githubusercontent.com/bkaping/expedia-lite/6de604f/docs/assignment3-part1-interface.svg)

The design shows the full intended path: choose a practice, complete/leave one canonical skill, then review concise history. A **Crisis support** control is visually present across all three states. It opens browser-local, static support information and therefore does not rely on the model, an API response, or a classifier decision.

## Research-to-design reasoning

The design note maps the supplied R1–R4 and D1–D6 findings to specific decisions and tradeoffs. The important choices are:

- Keep practices short because R1 reports attention falling after 90–100 seconds; measure exercise time separately from setup and voluntary pauses.
- Use a persistent support route for R2 rather than triggering it from a model or an unreliable inference.
- Make leaving neutral and easy in response to R3/R4; a stopped session is not treated as failure.
- Follow D1 by avoiding a claimed distress detector; everyone receives the same low-demand baseline and visible control.
- Follow D2/D3 with one canonical skill at a time and no required reflection, rating, or text entry.
- Follow D5 with an optional “use this practice again” shortcut based only on the latest completed skill. It never hides either skill or routes anyone automatically.
- Follow D6 with quiet visuals, short wording, keyboard-reachable controls, and a reduced-motion text-count alternative to the breathing cue.

## Proposed model, data, and history boundaries

The optional model contribution is deliberately narrow: after a completed practice, it may acknowledge an explicitly voluntary **fictional** note in one short, neutral response. The application—not the model—keeps control of skill steps, timing, exits, saved state, and support access. Unsafe, directive, diagnostic, medical, or overlong output is planned to be rejected in application code and replaced locally.

The proposed SQLite design stores an opaque session ID, selected skill, source, outcome, active seconds, and timestamps. It may also store an explicit optional fictional note, a bounded acknowledgment, and a model identifier. This supports a small history and optional last-skill shortcut without an account, diagnosis, score, location, inferred distress level, or stored potential-crisis text. The history shows the person what was saved without turning it into a judgment.

## What is complete and unresolved at this milestone

**Complete:** a research-grounded design for two skills, timing assumptions, visible interface concept, flow diagram, static independent support route, personalization/user-control rationale, bounded model role, proposed data model, redacted evidence record, and AI-use disclosure.

**Not yet complete:** a running application, SQLite schema, model request, support-resource localization check, browser/reduced-motion check, measured exercise run, failure-path evidence, fictional-scenario evaluation, or recordings. Those are intentionally deferred to Parts 3.2 and 3.3 and are not claimed as completed here.
