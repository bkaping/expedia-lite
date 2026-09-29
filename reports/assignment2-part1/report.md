# Wayfarer Lite — Assignment 2 Part 1 (preserved report)

The submitted Part 1 implementation and its report remain available at [commit 79c695c](https://github.com/bkaping/expedia-lite/blob/79c695c/report.md). This preserved copy keeps the required screenshot evidence in the current repository after the root `report.md` advances to Assignment 2 Part 2.

## Screenshot evidence

![Live Geoapify hotel results near ZIP 02108, including the synchronized list and map](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/live-results-map.png)

![A map-marker selection opens the matching provider-place popup](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/map-marker-selection.png)

![A list selection for Beacon Hill Hotel and Bistro highlights the card and opens the corresponding map popup](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/list-map-selection.png)

![Invalid three-digit ZIP input produces clear feedback](https://raw.githubusercontent.com/bkaping/expedia-lite/71a9add/screenshots/assignment2-part1/invalid-zip.png)

## Part 1 summary

FastAPI resolves an exact five-digit U.S. ZIP through Geoapify and returns nearby `accommodation.hotel` places within 5 km. Vue displays the returned provider names, addresses, and coordinates in a synchronized Leaflet map and result list. The application does not claim prices, ratings, availability, or bookings.
