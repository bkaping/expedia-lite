# Wayfarer Lite — Assignment 2 Part 1

## Project access

- Repository: [https://github.com/bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
- Assessed Part 1 implementation commit: [71a9add](https://github.com/bkaping/expedia-lite/commit/71a9add)
- Setup: follow the [README](README.md). Create a local root `.env` from [`.env.example`](.env.example), set `GEOAPIFY_API_KEY`, and do not commit, upload, or record the key.

## Implementation

The user enters an exact five-digit U.S. ZIP code. Vue owns the form, visible states, and synchronized list/map selection. FastAPI protects the Geoapify credential and exposes the local API. `GeoapifyHotelController` resolves the exact requested ZIP, then requests up to 20 nearby `accommodation.hotel` provider places within 5 km.

The application displays only provider names, addresses, and coordinates. It does not claim prices, ratings, room availability, or real bookings.

## Research and early mockup

The [research notes](docs/assignment2-part1-research.md) record sources, observed patterns, weaknesses, and decisions. The [early mockup](docs/assignment2-part1-mockup.svg) predates the implementation and shows the ZIP search, visible status, list, map, and shared selection design.

## Verification

| Action | Expected result | Observed result |
| --- | --- | --- |
| Search live ZIP `02108` | Resolve the exact U.S. ZIP and return nearby provider-listed hotels within 5 km. | On September 29, 2026, `02108` resolved to Boston, Massachusetts and returned 20 provider hotel places. |
| Enter invalid ZIP `123` | Clear validation feedback with no live request. | The browser displayed “Enter exactly five digits, including a leading zero when your ZIP code has one.” |
| Select a map marker | Open the matching provider-place popup. | The selected marker opened its name/address popup. |
| Select a list item | Highlight its card and open the corresponding map popup. | Selecting Beacon Hill Hotel and Bistro highlighted its card and opened the matching popup. |
| Simulate provider failure | Show a failure rather than a successful empty result. | Covered by focused backend test. |

## Screenshot evidence

![Live Geoapify hotel results near ZIP 02108, including the synchronized list and map](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/live-results-map.png)

![A map-marker selection opens the matching provider-place popup](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/map-marker-selection.png)

![A list selection for Beacon Hill Hotel and Bistro highlights the card and opens the corresponding map popup](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/list-map-selection.png)

![Invalid three-digit ZIP input produces clear feedback](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/invalid-zip.png)

## Demo video

Pending recording and accessible link. The Part 1 video should show a live ZIP search, list-to-map and map-to-list selection, and invalid ZIP feedback without showing the Geoapify key.

## Project context and next steps

See the [README](README.md), [project guidance](AGENTS.md), [design note](docs/design.md), [selected prompts](prompts/selected-prompts.md), and [current handoff](handoffs/current.md).

The live result count can change because Geoapify provider coverage changes. The next task was Assignment 2 Part 2: saving honest provider-place snapshots to SQLite without adding booking data.
