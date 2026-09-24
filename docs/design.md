# Design note — Wayfarer Lite

## Responsibilities

The Vue view owns the visible state: search text, returned stays, booking form values, feedback, and booking history. It sends every data operation through the FastAPI API; it does not read CSV or SQLite files.

FastAPI is the request boundary. It validates request shapes, exposes search and booking CRUD endpoints, translates domain errors into useful HTTP responses, and allows the local Vue development server through CORS.

The Python database controller is the model/controller layer. It owns schema setup, imports fixture CSV data only on the first successful run, joins hotels with stays, and makes create, read, update, and delete changes inside SQLite transactions. SQLite stores the durable state after seeding.

## Data relationships

`hotels (1) → trips/stays (many)` and `users (1) → bookings (many)`. A booking links one user, hotel, and trip. A confirmed booking consumes one room from its trip; cancellation and deletion return that room. Cancellation keeps the booking record; delete removes only the chosen test booking.

## Interface decisions

The screen follows the natural task sequence: search, book, then inspect history. Clear labels, a table caption, visible status chips, direct feedback, and an explicit delete confirmation support recognition and error prevention. It uses responsive layout and visible keyboard focus indicators so the same functions remain usable on a narrow screen or without a mouse.
