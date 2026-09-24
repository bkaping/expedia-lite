# Wayfarer Lite — Part 1

## Repository and commit

Repository URL: [https://github.com/bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
Submitted Part 1 commit: **Pending — create and record the Part 1 checkpoint commit before submission.**

## Implementation

Part 1 is the CSV-search version of Wayfarer Lite. The Vue frontend provides a hotel-name input and Search button, then displays matched hotels and their available stays in a labeled table. It also shows a clear no-results message.

For the Part 1 checkpoint, FastAPI should read `hotels.csv` and `trips.csv`, connect records using `hotel_id`, and return matching hotel/stay data to the Vue client. The provided data archive contains eight hotels and twelve trips, including Harbor Lantern Hotel (`H001`) with two available trips (`T001` and `T009`).

## Verification

| Action | Expected result | Observed result |
| --- | --- | --- |
| Search `Harbor Lantern` | The matching hotel and its two related stays appear in the labeled results table. | Pending manual browser check after the supplied CSV files are loaded into the Part 1 checkpoint. |
| Search a name that is not in the CSV data | A clear no-results message appears. | Pending manual browser check. |
| Review the Part 1 changes | The Vue client, FastAPI endpoint, CSV join, and table labels are readable and consistent. | Pending final VS Code review. |

Add repository-hosted screenshots after the manual checks:

- `[Successful CSV search screenshot](replace-with-accessible-repository-image-URL)`
- `[No-results screenshot](replace-with-accessible-repository-image-URL)`

## Project context and next steps

- [README](../../README.md)
- [Project guidance](../../AGENTS.md)
- [Design note](../../docs/design.md)
- [Selected prompts](../../prompts/selected-prompts.md)
- [Current handoff](../../handoffs/current.md)

Before submitting Part 1, import the supplied CSV fixtures from `expedia-lite-data (2).zip`, complete the manual checks, save screenshots in the repository, and replace the pending commit field with the exact Part 1 commit SHA.
