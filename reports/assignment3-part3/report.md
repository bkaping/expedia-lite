# Stillpoint — Assignment 3.3 refinement and evaluation

## Submission checkpoint

- Repository: `https://github.com/bkaping/expedia-lite`
- Implementation checkpoint: **replace with the verified Part 3.3 commit hash before upload**
- Run instructions: [README](../../README.md)
- Evaluation evidence: [15 scenarios and behavior checks](../../docs/assignment3-evaluation.md)
- Design/safety note: [design note](../../docs/design.md)
- Verification record: [verification record](../../docs/assignment3-verification.md)
- Recording script: [finished-demo and failure-investigation plan](../../docs/assignment3-recording-plan.md)
- AI-use disclosure: [AI-USE](../../AI-USE.md)

## Refinement from Part 3.2

The free-text companion was removed because it created unnecessary disclosure and review burden. The final design keeps fixed, factual website questions and adds one explicit, optional model-summary prompt after a completed fictional practice. This preserves a demonstrable model contribution and persistent conversation record without inviting open-ended emotional content.

The paced-breathing interface was also refined with automatic and tap-and-hold pacing. Both controls retain the exact six-cycle 4-in / 6-out sequence; releasing the hold control pauses rather than skipping or changing a step.

## Evaluation summary

Twenty-two automated backend tests passed, including fake-model context, failure, and unsafe-output checks. The frontend production build passed. Fifteen fictional scenarios and three cross-case behavior checks are recorded in the linked evaluation. Two fixed, no-profile live prompts were checked through the configured backend model; the provider/model varied between responses, while both replies remained within the local safety boundary.

The persistent support panel remains in the browser even if a model summary fails. Journal content remains separate from model context. Saved history shows neutral practice outcomes and any selected model-summary exchanges.

## Limits

The application is a localhost-only coursework prototype for fictional scenarios. It is not therapy, diagnosis, monitoring, crisis care, or something to rely on during distress. The two live outputs, automated checks, and a planned recording do not demonstrate clinical effectiveness, real-world usefulness, or peer usability.

## Recording note

The linked script is ready for the required demonstration and process screencast. Record the two sections locally and replace this note with accessible recording link(s) before course submission; that media cannot be truthfully claimed until it exists.
