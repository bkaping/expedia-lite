# Stillpoint — Assignment 3.2 Working Application and Safety

## Submission checkpoint and review links

- Repository: [bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
- **Submitted Part 3.2 implementation checkpoint:** [`8cd200bb71eca88bfb2d30d2d440985bb5dd1b49`](https://github.com/bkaping/expedia-lite/commit/8cd200bb71eca88bfb2d30d2d440985bb5dd1b49) — `feat: implement assignment 3 part 2 skills prototype`
- **Run instructions:** [README](https://github.com/bkaping/expedia-lite/blob/8cd200bb71eca88bfb2d30d2d440985bb5dd1b49/README.md)
- **Design and safety decisions:** [docs/design.md](https://github.com/bkaping/expedia-lite/blob/8cd200bb71eca88bfb2d30d2d440985bb5dd1b49/docs/design.md)
- **Verification record:** [docs/assignment3-verification.md](https://github.com/bkaping/expedia-lite/blob/8cd200bb71eca88bfb2d30d2d440985bb5dd1b49/docs/assignment3-verification.md)
- **Curated evidence:** [selected prompts](https://github.com/bkaping/expedia-lite/blob/8cd200bb71eca88bfb2d30d2d440985bb5dd1b49/prompts/selected-prompts.md) and [evidence log](https://github.com/bkaping/expedia-lite/blob/8cd200bb71eca88bfb2d30d2d440985bb5dd1b49/docs/evidence-log.md)
- **AI-use disclosure:** [AI-USE.md](https://github.com/bkaping/expedia-lite/blob/8cd200bb71eca88bfb2d30d2d440985bb5dd1b49/AI-USE.md)

All review links are pinned to the immutable implementation checkpoint above. This report is uploaded separately to the course site; the linked commit contains each referenced application and evidence artifact.

## What is complete

Stillpoint implements one complete study-provided skill: paced breathing (four seconds in, six seconds out, six cycles). The guided timer starts with the first active cue and records **60 active seconds** at completion. A person can pause or leave without explanation. Leaving before the first cue records a neutral stopped session with 0 active seconds; navigating to Saved history from an active practice also first saves a neutral stopped session so no active record is orphaned.

Vue owns the visible skill flow, pacing cue, exits, browser-local support panel, and history presentation. FastAPI owns SQLite and the optional model call. SQLite stores only minimal sessions and explicit optional fictional notes; history makes those records reviewable. The latest completed skill is offered only as an optional repeat shortcut, never as automatic routing.

The model contribution is deliberately narrow: after a completed session, it receives a voluntary **fictional** note and returns one short neutral acknowledgment. Application code—not the model—controls canonical skill steps, timing, exits, persistence, the support route, and output validation. A limited potential-crisis phrase rule prevents matching text from being saved verbatim or transmitted to the model; it is documented as an imperfect routing rule, not a distress detector.

## Evidence and failure behavior

All test scenarios and browser notes are fictional. On October 29, 2026, the full backend suite passed **16 tests** and the frontend production build passed. The focused Part 3.2 tests cover SQLite persistence, optional usual-skill behavior, fake-model note persistence, phrase redaction before a model call, and a local fallback for unsafe model output.

Browser checks confirmed that the static support dialog is present on the home and practice flows, uses no FastAPI/model request, and remains usable alongside the prototype. The original October 15 check observed a completed 60-second practice and one bounded acknowledgment (`Acknowledged.`) for the fictional note “I followed the fictional count.” The October 29 recheck confirmed that navigating away from an active practice writes a stopped session before history opens; a SQLite inspection of session metadata matched that record.

For a failure check, a separate localhost API was run with no model key. After a temporary completed fictional session, `POST /api/conversations` returned HTTP 503 with `companion_not_configured`; no provider call was made. The completed practice and browser-local support panel remain independent of that failure.

## Scope and remaining work

This is a coherent Part 3.2 coursework prototype, not a finished clinical tool. 5–4–3–2–1 grounding remains deliberately deferred and is not presented as available in the running interface. Part 3.3 must add the required 15 fictional scenarios, three explicit cross-case behavior checks, broader mocked/live-model comparison, reduced-motion and keyboard evidence, a surprising finding, an untested limitation, and the finished-demo plus failure-investigation recordings. No real-person distress scenario was used.
