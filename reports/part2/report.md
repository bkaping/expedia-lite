# Wayfarer Lite — Part 2

## Repository and commit

Repository URL: [https://github.com/bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
Submitted Part 2 implementation commit: [6b75638](https://github.com/bkaping/expedia-lite/commit/6b75638)
Part 1 checkpoint: **Pending — create and record the Part 1 checkpoint commit before submission.**

## Implementation

Part 2 extends the search flow with a responsive booking interface and SQLite persistence. Vue presents search results, a simulated booking form, booking history, status feedback, cancellation, and test-booking deletion. FastAPI validates requests and exposes endpoints for search and booking CRUD. The Python database controller creates the SQLite schema, seeds it only once, and performs later reads and writes in SQLite transactions.

The data model connects hotels to stays and users to bookings. Creating a confirmed booking consumes one available room; cancelling it preserves the booking record and returns the room; deleting a confirmed test booking removes it and returns the room. Browser refreshes and backend restarts preserve the SQLite data without duplicating starter records.

## Verification

| Action | Expected result | Observed result |
| --- | --- | --- |
| Search a matching hotel | A matching hotel and its stays appear in a labeled table. | Verified in the local browser using the current development fixture data. |
| Search a nonmatching hotel | A clear no-results message appears. | Verified in the local browser. |
| Create a booking | The booking appears in history and available rooms decrease. | Verified in the local browser against an isolated SQLite database. |
| Cancel a booking | Its status becomes cancelled and the record remains in history. | Verified in the local browser against an isolated SQLite database. |
| Delete a test booking | The selected record is removed from history. | Verified through the FastAPI endpoint and controller tests; repeat the visible frontend delete action before submission. |
| Refresh and restart | Existing changes remain and starter records are not duplicated. | Browser refresh and controller tests verified persistence. |

Add repository-hosted screenshots after the final manual checks:

- `[Search result and booking screenshot](replace-with-accessible-repository-image-URL)`
- `[No-results screenshot](replace-with-accessible-repository-image-URL)`
- `[Booking history CRUD screenshot](replace-with-accessible-repository-image-URL)`

## Project context and next steps

- [README](../../README.md)
- [Project guidance](../../AGENTS.md)
- [Design note](../../docs/design.md)
- [Selected prompts](../../prompts/selected-prompts.md)
- [Current handoff](../../handoffs/current.md)

The supplied archive is now available, but its CSV schema has not yet been integrated into the local application. Before final submission, replace the development fixture data with the supplied hotel, trip, user, and booking rows; run the complete frontend CRUD verification with that data; add screenshots; create the required Part 1 and Part 2 commits; and replace the pending commit fields above.
