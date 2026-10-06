# Local simulation design note

The Geoapify live API supplies hotel-place names, addresses, place IDs, and coordinates. It does not supply booking prices or room inventory.

When a user saves a provider place, FastAPI derives a stable local simulated nightly rate and available-room count from that provider place ID, then stores both values in SQLite with the saved snapshot. A repeat save keeps the original row and its original simulations.

Vue labels both values as **Simulated** and states that they are local, not provider prices, live availability, or booking confirmation. The refresh control reads the saved list from SQLite and reports that database read in the interface.

Existing local shortlist databases are migrated at application startup. Legacy saved rows receive simulations without replacing their provider name, address, coordinates, or timestamp.
