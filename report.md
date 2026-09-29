# Wayfarer Lite — Assignment 2 Part 1

## Project access

- Repository: [https://github.com/bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
- Assessed implementation commit: [71a9add](https://github.com/bkaping/expedia-lite/commit/71a9add)
- Setup: follow the [README](README.md). Create a local root `.env` from [`.env.example`](.env.example) and set `GEOAPIFY_API_KEY`; do not commit, upload, or record the real value.

## Research notes

The [research notes](docs/assignment2-part1-research.md) record sources, observed patterns, weaknesses, and resulting decisions. The design keeps a result list and map visible together, uses an exact U.S. ZIP-resolution step before the 5 km hotel search, and presents provider data without inventing booking details.

## Early mockup

![Early list and map interaction mockup](docs/assignment2-part1-mockup.svg)

The mockup predates the final implementation. The implemented screen preserves its ZIP search, visible status, side-by-side list and map, and shared selection state; it adds explicit provider-limit wording and visible OpenStreetMap attribution.

## Screen-recorded demo video

Pending recording and accessible link. The video will show a real ZIP lookup, synchronized list-to-marker and marker-to-list selection, and invalid-input feedback. It will not display a credential.

## Verification record

| Action | Expected result | Observed result |
| --- | --- | --- |
| Review the changed files in VS Code | MVC roles, local credential handling, research, mockup, and tests are clear. | Completed: Vue owns view state and selection; FastAPI owns the protected request boundary; the controller maps Geoapify data into live-place models. |
| Live search `02108` on September 29, 2026 | The exact U.S. ZIP resolves before a hotel search within 5 km of that returned coordinate. | Observed: `02108` resolved to Boston, Massachusetts and returned 20 Geoapify hotel places. One provider record lacked a name, so the interface will honestly label it rather than invent one. |
| Invalid input `123` | Clear invalid-input message; no provider request. | Observed in the browser: the screen displayed “Enter exactly five digits, including a leading zero when your ZIP code has one.” |
| Provider request failure | Clear service-failure message, not a successful empty list. | Covered by focused controller test using a simulated provider failure. |
| Select a hotel marker | The matching provider marker opens its popup and identifies that place. | Observed in the browser: a selected marker opened the provider-name/address popup. |
| Select a list card | The matching map marker and popup identify the same provider place. | Observed in the browser: selecting Beacon Hill Hotel and Bistro highlighted its card and opened its matching popup on the map. |

The result count is not treated as fixed: live provider coverage can change. The application limits a request to 20 places and does not claim an exhaustive hotel inventory.

## Screenshot evidence

![Live Geoapify hotel results near ZIP 02108, including the synchronized list and map](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/live-results-map.png)

![A map-marker selection opens the matching provider-place popup](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/map-marker-selection.png)

![A list selection for Beacon Hill Hotel and Bistro highlights the card and opens the corresponding map popup](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/list-map-selection.png)

![Invalid three-digit ZIP input produces clear feedback](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/invalid-zip.png)

## AI disclosure and evidence log

- OpenAI Codex (GPT-5) assisted with implementation, tests, documentation, and the local verification workflow.
- Selected prompt excerpts are in [prompts/selected-prompts.md](prompts/selected-prompts.md); they correspond to the controller, Vue map/list behavior, tests, and reliability decision.
- Evidence includes the [design note](docs/design.md), [research notes and mockup](docs/assignment2-part1-research.md), [current handoff](handoffs/current.md), and source/test changes in this repository.
- Revised approach: the first live request failed before reaching Geoapify because the local Python TLS store could not verify the certificate. After CHECK → approval → TAKE ACTION, `certifi` was added to the backend requirements and used only for the trusted CA bundle. The repeated real ZIP lookup succeeded without logging the credential.

## Remaining limits and next step

The implementation is limited to provider-listed hotel places within 5 km and does not make booking or inventory claims. Record the required live browser demo, add its accessible link above, and upload this file as `report.md` to the Assignment 2 Part 1 submission page.
