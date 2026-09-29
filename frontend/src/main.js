import { createApp, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './style.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

const markerIcon = (selected) =>
  L.divIcon({
    className: 'hotel-marker-wrapper',
    html: `<span class="hotel-marker${selected ? ' is-selected' : ''}" aria-hidden="true">H</span>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  })

const popupContent = (hotel) => {
  const content = document.createElement('div')
  const title = document.createElement('strong')
  const address = document.createElement('p')
  title.textContent = hotel.name
  address.textContent = hotel.address
  content.append(title, address)
  return content
}

const App = {
  setup() {
    const zipCode = ref('')
    const searchState = ref('idle')
    const statusMessage = ref('Enter a five-digit U.S. ZIP code to start a live search.')
    const searchData = ref(null)
    const selectedPlaceId = ref('')
    const mapElement = ref(null)
    const shortlist = ref([])
    const shortlistLoading = ref(true)
    const shortlistMessage = ref('')
    const shortlistProblem = ref('')

    let map
    let centerMarker
    const hotelMarkers = new Map()

    const clearMapResults = () => {
      hotelMarkers.forEach((marker) => marker.remove())
      hotelMarkers.clear()
      centerMarker?.remove()
      centerMarker = undefined
    }

    const updateMarkerSelection = () => {
      hotelMarkers.forEach((marker, placeId) => {
        marker.setIcon(markerIcon(placeId === selectedPlaceId.value))
      })
    }

    const selectHotel = (hotel, shouldFocusCard = false) => {
      selectedPlaceId.value = hotel.provider_place_id
      updateMarkerSelection()
      const marker = hotelMarkers.get(hotel.provider_place_id)
      if (marker) {
        marker.openPopup()
        map.panTo(marker.getLatLng())
      }
      if (shouldFocusCard) {
        window.setTimeout(() => document.getElementById(`hotel-${hotel.provider_place_id}`)?.focus(), 0)
      }
    }

    const drawMapResults = async () => {
      clearMapResults()
      if (!map || !searchData.value) return

      const { center, hotels } = searchData.value
      centerMarker = L.circleMarker([center.latitude, center.longitude], {
        color: '#304f96',
        fillColor: '#9fb7f4',
        fillOpacity: 0.95,
        radius: 8,
        weight: 3,
      })
        .addTo(map)
        .bindTooltip(`Search center: ${center.label}`, { direction: 'top' })

      hotels.forEach((hotel) => {
        const marker = L.marker([hotel.latitude, hotel.longitude], {
          icon: markerIcon(hotel.provider_place_id === selectedPlaceId.value),
          keyboard: true,
          title: hotel.name,
        })
          .addTo(map)
          .bindPopup(popupContent(hotel))
          .on('click', () => selectHotel(hotel, true))
        hotelMarkers.set(hotel.provider_place_id, marker)
      })

      await nextTick()
      map.invalidateSize()
      const points = [[center.latitude, center.longitude], ...hotels.map((hotel) => [hotel.latitude, hotel.longitude])]
      map.fitBounds(L.latLngBounds(points), { padding: [36, 36], maxZoom: 13 })
    }

    const errorMessage = async (response) => {
      try {
        const payload = await response.json()
        if (typeof payload.detail === 'object') return payload.detail.message
        return payload.detail
      } catch {
        return 'The live hotel service did not return a usable response.'
      }
    }

    const isSaved = (hotel) =>
      shortlist.value.some((place) => place.provider_place_id === hotel.provider_place_id)

    const loadShortlist = async () => {
      shortlistLoading.value = true
      shortlistProblem.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/shortlist`)
        if (!response.ok) throw new Error(await errorMessage(response))
        shortlist.value = await response.json()
      } catch (error) {
        shortlistProblem.value = error.message || 'The saved shortlist could not be loaded.'
      } finally {
        shortlistLoading.value = false
      }
    }

    const saveToShortlist = async (hotel) => {
      shortlistMessage.value = ''
      shortlistProblem.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/shortlist`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            provider_place_id: hotel.provider_place_id,
            name: hotel.name,
            address: hotel.address,
            latitude: hotel.latitude,
            longitude: hotel.longitude,
          }),
        })
        if (!response.ok) throw new Error(await errorMessage(response))
        const result = await response.json()
        if (result.created) shortlist.value = [result.place, ...shortlist.value]
        shortlistMessage.value = result.created
          ? `${result.place.name} was saved to your persistent shortlist.`
          : `${result.place.name} is already in your shortlist.`
      } catch (error) {
        shortlistProblem.value = error.message || 'This provider place could not be saved.'
      }
    }

    const removeFromShortlist = async (place) => {
      if (!window.confirm(`Remove ${place.name} from your shortlist?`)) return
      shortlistMessage.value = ''
      shortlistProblem.value = ''
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/shortlist/${encodeURIComponent(place.provider_place_id)}`,
          { method: 'DELETE' },
        )
        if (!response.ok) throw new Error(await errorMessage(response))
        shortlist.value = shortlist.value.filter((item) => item.provider_place_id !== place.provider_place_id)
        shortlistMessage.value = `${place.name} was removed from your shortlist.`
      } catch (error) {
        shortlistProblem.value = error.message || 'This saved place could not be removed.'
      }
    }

    const formatSavedAt = (timestamp) =>
      new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(
        new Date(timestamp),
      )

    const search = async () => {
      const requestedZip = zipCode.value.trim()
      selectedPlaceId.value = ''
      searchData.value = null
      clearMapResults()

      if (!/^\d{5}$/.test(requestedZip)) {
        searchState.value = 'invalid'
        statusMessage.value = 'Enter exactly five digits, including a leading zero when your ZIP code has one.'
        return
      }

      searchState.value = 'loading'
      statusMessage.value = `Looking up ZIP code ${requestedZip} and nearby provider-listed hotels…`
      try {
        const response = await fetch(`${API_BASE_URL}/api/live-hotels?zip_code=${encodeURIComponent(requestedZip)}`)
        if (!response.ok) {
          const message = await errorMessage(response)
          if (response.status === 404) {
            searchState.value = 'unresolved'
          } else if (response.status === 429) {
            searchState.value = 'rate-limited'
          } else {
            searchState.value = 'failed'
          }
          statusMessage.value = message
          return
        }
        searchData.value = await response.json()
        if (searchData.value.hotels.length === 0) {
          searchState.value = 'empty'
          statusMessage.value = `ZIP code ${requestedZip} resolved to ${searchData.value.center.label}, but Geoapify returned no nearby hotel places within 5 km.`
        } else {
          searchState.value = 'results'
          statusMessage.value = `${searchData.value.hotels.length} provider-listed hotel${searchData.value.hotels.length === 1 ? '' : 's'} near ${searchData.value.center.label}. Select a list item or map marker to connect both views.`
        }
        await drawMapResults()
      } catch {
        searchState.value = 'failed'
        statusMessage.value = 'The live hotel request could not reach this application. Check that the backend is running, then try again.'
      }
    }

    onMounted(() => {
      map = L.map(mapElement.value, { scrollWheelZoom: true }).setView([39.8283, -98.5795], 4)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map)
      loadShortlist()
    })

    onBeforeUnmount(() => map?.remove())

    return {
      formatSavedAt,
      isSaved,
      loadShortlist,
      mapElement,
      removeFromShortlist,
      saveToShortlist,
      search,
      searchData,
      searchState,
      selectHotel,
      selectedPlaceId,
      shortlist,
      shortlistLoading,
      shortlistMessage,
      shortlistProblem,
      statusMessage,
      zipCode,
    }
  },
  template: `
    <main class="shell">
      <header class="hero">
        <p class="eyebrow">ASSIGNMENT 2 · PART 2</p>
        <h1>Wayfarer Lite</h1>
        <p class="lede">Explore provider-listed hotels near a U.S. ZIP code.</p>
      </header>

      <section class="search-panel" aria-labelledby="search-heading">
        <div>
          <p class="eyebrow">LIVE HOTEL SEARCH</p>
          <h2 id="search-heading">Search around a ZIP code</h2>
        </div>
        <form class="search-form" @submit.prevent="search">
          <label for="zip-code">Five-digit U.S. ZIP code</label>
          <div class="search-controls">
            <input id="zip-code" v-model="zipCode" inputmode="numeric" autocomplete="postal-code" maxlength="5" placeholder="e.g., 02108" aria-describedby="live-status" />
            <button class="primary" type="submit" :disabled="searchState === 'loading'">{{ searchState === 'loading' ? 'Searching…' : 'Search hotels' }}</button>
          </div>
        </form>
        <p id="live-status" class="status-message" :class="searchState" role="status" aria-live="polite">{{ statusMessage }}</p>
      </section>

      <section class="explorer" aria-label="Live hotel search results">
        <div class="results-panel">
          <div class="results-heading">
            <div>
              <p class="eyebrow">RESULT LIST</p>
              <h2>Nearby hotel places</h2>
            </div>
            <p v-if="searchData" class="result-note">Up to {{ searchData.result_limit }} places within {{ searchData.radius_meters / 1000 }} km</p>
          </div>

          <p v-if="!searchData && searchState === 'idle'" class="empty-copy">Your live provider results will appear here after a ZIP search.</p>
          <p v-else-if="searchState === 'empty'" class="empty-copy">No nearby hotel places were returned for this resolved search center.</p>
          <ol v-else-if="searchData" class="hotel-list">
            <li v-for="hotel in searchData.hotels" :key="hotel.provider_place_id">
              <article class="hotel-card" :class="{ selected: selectedPlaceId === hotel.provider_place_id }">
                <button
                  :id="'hotel-' + hotel.provider_place_id"
                  class="hotel-select"
                  type="button"
                  :aria-pressed="selectedPlaceId === hotel.provider_place_id"
                  @click="selectHotel(hotel)"
                >
                  <strong>{{ hotel.name }}</strong>
                  <span>{{ hotel.address }}</span>
                  <small v-if="selectedPlaceId === hotel.provider_place_id">Selected on map</small>
                </button>
                <button class="save-button" :class="{ saved: isSaved(hotel) }" type="button" @click="saveToShortlist(hotel)">
                  {{ isSaved(hotel) ? 'Already saved — check again' : 'Save to shortlist' }}
                </button>
              </article>
            </li>
          </ol>
          <p v-if="searchData" class="provider-note">Names, addresses, and map points come from Geoapify. Results may be incomplete or change over time; this app does not show prices, ratings, availability, or booking confirmation.</p>
        </div>

        <div class="map-panel">
          <div class="map-label"><span class="center-dot" aria-hidden="true"></span> Search center <span class="hotel-dot" aria-hidden="true">H</span> Hotel place</div>
          <div ref="mapElement" class="map" aria-label="Map of nearby hotel places"></div>
        </div>
      </section>

      <section class="shortlist-panel" aria-labelledby="shortlist-heading">
        <div class="shortlist-heading">
          <div>
            <p class="eyebrow">PART 2 · SQLITE PERSISTENCE</p>
            <h2 id="shortlist-heading">Saved shortlist</h2>
          </div>
          <button class="quiet-button" type="button" :disabled="shortlistLoading" @click="loadShortlist">Refresh saved places</button>
        </div>
        <p class="shortlist-intro">These are saved provider snapshots. They remain recognizable after a browser or backend restart, even if a later live search changes.</p>
        <p v-if="shortlistMessage" class="shortlist-message success" role="status">{{ shortlistMessage }}</p>
        <p v-if="shortlistProblem" class="shortlist-message error" role="alert">{{ shortlistProblem }}</p>
        <p v-if="shortlistLoading" class="shortlist-message">Loading saved places…</p>
        <p v-else-if="!shortlist.length" class="shortlist-message">No saved places yet. Use “Save to shortlist” on a live provider result.</p>
        <ol v-else class="shortlist-list">
          <li v-for="place in shortlist" :key="place.provider_place_id" class="shortlist-card">
            <div>
              <h3>{{ place.name }}</h3>
              <p>{{ place.address }}</p>
              <small>Provider snapshot saved {{ formatSavedAt(place.saved_at) }}</small>
            </div>
            <button class="remove-button" type="button" @click="removeFromShortlist(place)">Remove</button>
          </li>
        </ol>
      </section>
    </main>
  `,
}

createApp(App).mount('#app')
