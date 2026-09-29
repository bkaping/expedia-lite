# Wayfarer Lite — Assignment 2 Part 2

## Project access and assessed commit

- Repository: [https://github.com/bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
- Assessed Part 2 implementation commit: [d8c39eb](https://github.com/bkaping/expedia-lite/commit/d8c39eb)
- Startup instructions: [README.md](README.md). Create root `.env` from [`.env.example`](.env.example), set `GEOAPIFY_API_KEY` locally, and never commit or record that key.
- Fixed Part 2 verification fixture: [`backend/data/assignment2-shortlist-sample.json`](backend/data/assignment2-shortlist-sample.json). It is labeled fixed sample data, not a live Geoapify response.

## Part 1 foundation

Part 1 accepts an exact five-digit U.S. ZIP code, resolves it through Geoapify, and shows nearby `accommodation.hotel` provider places within 5 km in a synchronized Leaflet list and map. It presents only provider names, addresses, and coordinates; it does not claim prices, ratings, availability, or bookings.

The preserved [Assignment 2 Part 1 report](reports/assignment2-part1/report.md) includes the four required browser screenshots: live list/map results, marker selection, list-to-map selection, and invalid ZIP feedback. The original submitted report is also available at [commit 79c695c](https://github.com/bkaping/expedia-lite/blob/79c695c/report.md).

## Research and early mockup

- [Part 1 research and mockup](docs/assignment2-part1-research.md)
- [Part 2 research and early shortlist mockup](docs/assignment2-part2-research.md)
- [Current MVC/data-structure design note](docs/design.md)

The Part 2 research compares direct place-saving and separate saved-list patterns, then records the SQLite uniqueness tradeoff. The early mockup shows a save control beside each live result and a separate saved-shortlist area below the list/map interface.

![Part 2 early shortlist mockup](docs/assignment2-part2-mockup.svg)

## Part 2 implementation

Vue adds a **Save to shortlist** action to each current live provider result, a persistent **Saved shortlist** view, a refresh action, and a confirmation before removing an item. FastAPI keeps the browser away from the Geoapify key and provides dedicated shortlist endpoints. `ShortlistController` stores provider place ID, provider name, address, latitude, longitude, and timestamp in local SQLite.

Provider place ID is the SQLite primary key. `INSERT OR IGNORE` prevents a duplicate save and preserves the first stored provider snapshot even if a later live response changes its name or address. The generated database `backend/data/assignment2_shortlist.db` is ignored by Git. It deliberately stores no rate, price, room availability, rating, or booking data.

## Verification record

| Action | Expected result | Observed result |
| --- | --- | --- |
| Run the fixed JSON fixture through a save request | One provider snapshot is stored. | Observed: the initial POST returned `created: true` with Beacon Hill Hotel and Bistro’s fixture name/address. |
| Repeat the save using the same provider place ID but changed name/address | The database prevents the duplicate and retains the first snapshot. | Observed: the second POST returned `created: false` and still returned the original Beacon Hill Hotel and Bistro snapshot. |
| Restart FastAPI using the same temporary SQLite file | The saved snapshot remains available after restart. | Observed: `GET /api/shortlist` returned the previously saved provider record after backend restart. |
| Remove that saved record | The individual record is removed. | Observed: the DELETE endpoint succeeded; a follow-up `GET /api/shortlist` returned `[]`. |
| Run focused backend tests | CSV search, live-state, duplicate, persistence, and removal tests pass. | Observed: `python3 -m unittest discover -s backend/tests -v` passed all 8 tests. |
| Build the frontend for production | Vue compiles successfully. | Observed: `npm run build` from `frontend/` completed successfully. |
| Simulate a provider failure and an empty provider result | Failure stays a failure; a true empty response stays a successful empty result. | Observed: both focused controller tests pass without consuming the live API quota. |
| Review Part 1 live browser evidence | ZIP input, provider list/map sync, selections, and invalid input are visible. | Observed: all four screenshots are embedded in the preserved Part 1 report linked above. |

## Demo video (under three minutes)

Pending recording. Record a short local browser demo with no credential visible: search `02108`; save one returned hotel; show it in **Saved shortlist**; try saving it again to show the duplicate message; refresh the browser or restart FastAPI and show it remains; then remove it. Add the accessible video link here before submission.

## AI disclosure and supporting evidence

- OpenAI Codex (GPT-5) assisted with implementation, tests, documentation, and local verification.
- The [selected prompts](prompts/selected-prompts.md) include the initial implementation requests, test request, and the revised approach that moved duplicate prevention from a browser-only cue to SQLite `INSERT OR IGNORE`.
- The [current handoff](handoffs/current.md) summarizes what is checked and what remains for the student-recorded demo.

## Remaining limitation and next step

The shortlist is local to this application’s SQLite database and saves provider snapshots, not bookings. Record the required video, paste its accessible link above, then upload this `report.md` from the repository root to the Assignment 2 Part 2 submission page.
