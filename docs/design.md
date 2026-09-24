# Design note — Wayfarer Lite Part 1

## Responsibilities

The Vue view owns the visible search text, matching hotel rows, loading state, and no-results feedback. It sends a hotel-name query to FastAPI; it does not read CSV files itself.

FastAPI is the request boundary. It validates the hotel-name query, exposes the search endpoint, returns matching hotels, and allows the local Vue development server through CORS.

The Python CSV search controller is the model/controller layer for Part 1. It reads the supplied `hotels.csv` file using UTF-8 BOM-safe decoding and filters hotel names case-insensitively. The returned model contains the hotel ID, name, city, state, and nightly rate.

## Interface decisions

The screen centers one task: search for a hotel. Clear labels, a labeled results table, direct no-results feedback, responsive layout, and visible keyboard focus indicators make the required workflow easy to demonstrate.
