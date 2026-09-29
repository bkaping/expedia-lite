# Selected prompts — Assignment 2, Part 1

## Live search implementation

> Extend the existing Vue and FastAPI hotel project so a traveler enters a five-digit U.S. ZIP code, FastAPI resolves that exact U.S. postcode through Geoapify, and the frontend shows nearby provider hotel places in a synchronized list and Leaflet map. Keep the key backend-only and never invent hotel fields that Geoapify did not return.

## Verification and reliability

> Distinguish invalid input, unresolved ZIPs, successful empty results, provider failures, and rate limits in the interface. Add focused controller tests that mock provider responses, including a provider failure that must not be displayed as an empty result.

## Revised approach

> After a real Geoapify request failed with Python TLS certificate verification, check the local environment, obtain approval for the smallest reproducible dependency, use its CA bundle in the backend-only request, and repeat the live ZIP verification without logging credentials.
