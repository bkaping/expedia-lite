# Wayfarer Lite — Part 1

## Repository and commit

Repository URL: [https://github.com/bkaping/expedia-lite](https://github.com/bkaping/expedia-lite)
Submitted Part 1 implementation commit: [82d43ec](https://github.com/bkaping/expedia-lite/commit/82d43ec)

## Implementation

Part 1 is the CSV-search version of Wayfarer Lite. The Vue frontend provides a hotel-name input and Search button, then displays matched hotels and their available stays in a labeled table. It also shows a clear no-results message.

FastAPI reads the supplied `hotels.csv` file and returns matching hotel records to the Vue client. The provided data set contains eight hotels, including Harbor Lantern Hotel (`H001`), Maple Square Inn (`H002`), and Metro Garden Hotel (`H003`). The remaining supplied CSV files are preserved for Part 2.

## Verification

| Action | Expected result | Observed result |
| --- | --- | --- |
| Search `Harbor` | Harbor Lantern Hotel appears in the labeled results table with Boston, MA, and a $150 nightly rate. | Observed in the local browser. |
| Search a name that is not in the CSV data | A clear no-results message appears. | Observed in the local browser: `No hotels matched “Atlantis”. Try another hotel name.` |
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

Before submitting Part 1, complete the manual checks, save screenshots in the repository, and replace the pending commit field with the exact Part 1 commit SHA.
