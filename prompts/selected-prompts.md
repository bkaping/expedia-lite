# Selected prompts — Assignment 2

## Live search implementation

> Extend the existing Vue and FastAPI hotel project so a traveler enters a five-digit U.S. ZIP code, FastAPI resolves that exact U.S. postcode through Geoapify, and the frontend shows nearby provider hotel places in a synchronized list and Leaflet map. Keep the key backend-only and never invent hotel fields that Geoapify did not return.

## Verification and reliability

> Distinguish invalid input, unresolved ZIPs, successful empty results, provider failures, and rate limits in the interface. Add focused controller tests that mock provider responses, including a provider failure that must not be displayed as an empty result.

## Revised approach

> After a real Geoapify request failed with Python TLS certificate verification, check the local environment, obtain approval for the smallest reproducible dependency, use its CA bundle in the backend-only request, and repeat the live ZIP verification without logging credentials.

## Persistent shortlist implementation — Part 2

> Extend the existing live provider-place screen with a Save to shortlist action on each current result and a separate saved-list view. Persist only provider place ID, name, address, coordinates, and saved timestamp in SQLite. Prevent duplicate provider IDs at the database layer, preserve the first saved snapshot, and allow an individual remove action after confirmation.

## Repeatable persistence verification — Part 2

> Add a clearly labeled fixed JSON sample that is not live provider data. Use it in focused tests to prove save, duplicate prevention, persistence after reopening SQLite, and removal. Keep the previous mocked live-provider failure coverage so an external service failure cannot be mistaken for an empty successful response.

## Revised interaction approach — Part 2

> Do not rely only on disabling the browser save button to prevent duplicates. Treat the button as a helpful cue, but implement SQLite `INSERT OR IGNORE` with provider place ID as the primary key so repeated API requests cannot create two saved records or overwrite the earlier provider snapshot.

## Local simulation extension

> Extend the saved API-hotel model with a backend-generated, deterministic simulated nightly rate and simulated available-room count. Persist those fields in SQLite, migrate existing local shortlist rows safely, display the values only with explicit “Simulated” wording, and verify that a browser refresh reads the saved values back from the database.

## Grounded RAG hotel assistant — Part 2 revision

> Add a backend-only two-call LLM workflow for questions about saved hotels. First, give the model the exact SQLite schema and require JSON containing one read-only SELECT proposal. Validate and cap that SQL before executing it under a SQLite read-only authorizer. Then send the original question and exact retrieved records to the model again for a concise grounded answer. Return every stage to Vue for review and never expose the provider key to the browser.
