# Wayfarer Lite — Part 2

## Repository and commit

Repository URL: [https://github.com/bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
Submitted Part 2 commit: `[replace with the reviewed, merged commit SHA]`
Part 1 checkpoint: `[replace with the Part 1 commit SHA]`

## Implementation

Wayfarer Lite provides a hotel-name search, simulated booking, and booking history flow. The Vue frontend presents the search table, booking form, cancellation, deletion, and feedback. FastAPI validates requests and provides the communication boundary. A Python database controller initializes SQLite from CSV only once and performs all later hotel, stay, user, and booking reads and writes through SQLite.

Since Part 1, the application adds SQLite persistence, starter-data seeding, booking creation, durable history, cancellation that retains the record, test-booking deletion, status feedback, and an improved responsive interface.

## Verification

| Action | Expected result | Observed result |
| --- | --- | --- |
| Search `Maple` | A matching hotel and its available stays appear in a labeled table. | Observed in the local browser: Maple House Inn displayed two labeled stay rows. Controller tests also confirm a joined hotel/stay search. |
| Search a nonmatching name | A clear no-results message appears. | Observed in the local browser: `No hotels matched “No such hotel”. Try another name.` |
| Create a booking | The new booking is added to history and a room is consumed. | Observed in the local browser: a new Maple booking appeared in history and availability decreased from 3 to 2. |
| Cancel a booking | Status becomes cancelled while the booking remains in history and a room is returned. | Observed in the local browser: Booking #3 changed to Cancelled and remained visible in history. |
| Delete a test booking | The selected booking is removed from history and a room is returned if it was confirmed. | Automated API and controller checks successfully deleted an isolated test booking; repeat the visible **Delete test booking** action and capture it before submission. |
| Restart persistence | Existing data changes are retained and fixture rows are not duplicated. | The browser retained a newly created booking after refresh. Controller tests initialize twice and reopen the same database without duplicate seed bookings. |

Add accessible repository-hosted screenshots here after manually completing the browser checks:

- `[Search success screenshot](replace-with-accessible-repository-image-URL)`
- `[No-results screenshot](replace-with-accessible-repository-image-URL)`
- `[CRUD history screenshot](replace-with-accessible-repository-image-URL)`

## Project context and next steps

- [README](README.md)
- [Project guidance](AGENTS.md)
- [Design note](docs/design.md)
- [Selected prompts](prompts/selected-prompts.md)
- [Current handoff](handoffs/current.md)

The source data currently consists of labeled demo fixtures because the supplied course CSV files were not included in this workspace. Replace those records, run the browser verification, add screenshots and actual Git references, then commit the reviewed Part 1 and Part 2 checkpoints as required by the assignment.
