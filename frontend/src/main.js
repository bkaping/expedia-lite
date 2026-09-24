import { computed, onMounted, reactive, ref } from 'vue'
import { createApp } from 'vue'
import './style.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

const App = {
  setup() {
    const query = ref('')
    const searchResults = ref([])
    const searched = ref(false)
    const searching = ref(false)
    const searchError = ref('')
    const selectedStay = ref(null)
    const bookings = ref([])
    const bookingLoading = ref(false)
    const bookingError = ref('')
    const confirmation = ref('')
    const bookingForm = reactive({
      user_id: 1,
      guest_name: 'Alex Morgan',
      guests: 1,
    })

    const flattenedStays = computed(() =>
      searchResults.value.flatMap((hotel) =>
        hotel.stays.map((stay) => ({ ...stay, hotel_name: hotel.name, city: hotel.city })),
      ),
    )

    const formatMoney = (amount) =>
      new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

    const formatDate = (isoDate) =>
      new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(
        new Date(`${isoDate}T12:00:00`),
      )

    const getErrorMessage = async (response, defaultMessage) => {
      try {
        const body = await response.json()
        return body.detail ?? defaultMessage
      } catch {
        return defaultMessage
      }
    }

    const search = async ({ preserveFeedback = false } = {}) => {
      const term = query.value.trim()
      searched.value = true
      searchError.value = ''
      if (!preserveFeedback) confirmation.value = ''
      selectedStay.value = null
      if (!term) {
        searchResults.value = []
        searchError.value = 'Enter a hotel name to search.'
        return
      }
      searching.value = true
      try {
        const response = await fetch(`${API_BASE_URL}/api/search?hotel_name=${encodeURIComponent(term)}`)
        if (!response.ok) throw new Error(await getErrorMessage(response, 'Search could not be completed.'))
        searchResults.value = await response.json()
      } catch (error) {
        searchResults.value = []
        searchError.value = error.message
      } finally {
        searching.value = false
      }
    }

    const selectStay = (stay) => {
      bookingError.value = ''
      confirmation.value = ''
      selectedStay.value = stay
      window.setTimeout(() => document.querySelector('#booking-form')?.focus(), 0)
    }

    const loadBookings = async () => {
      bookingLoading.value = true
      bookingError.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/bookings`)
        if (!response.ok) throw new Error(await getErrorMessage(response, 'Booking history could not be loaded.'))
        bookings.value = await response.json()
      } catch (error) {
        bookingError.value = error.message
      } finally {
        bookingLoading.value = false
      }
    }

    const submitBooking = async () => {
      if (!selectedStay.value) return
      bookingLoading.value = true
      bookingError.value = ''
      confirmation.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/bookings`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...bookingForm,
            hotel_id: selectedStay.value.hotel_id,
            trip_id: selectedStay.value.id,
            guests: Number(bookingForm.guests),
            user_id: Number(bookingForm.user_id),
          }),
        })
        if (!response.ok) throw new Error(await getErrorMessage(response, 'Booking could not be created.'))
        const booking = await response.json()
        bookings.value = [booking, ...bookings.value]
        confirmation.value = `Booking #${booking.id} is confirmed and is now in your history.`
        selectedStay.value = null
        await search({ preserveFeedback: true })
      } catch (error) {
        bookingError.value = error.message
      } finally {
        bookingLoading.value = false
      }
    }

    const cancelBooking = async (booking) => {
      bookingLoading.value = true
      bookingError.value = ''
      confirmation.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/bookings/${booking.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'cancelled' }),
        })
        if (!response.ok) throw new Error(await getErrorMessage(response, 'Booking could not be cancelled.'))
        const updatedBooking = await response.json()
        bookings.value = bookings.value.map((item) => (item.id === booking.id ? updatedBooking : item))
        confirmation.value = `Booking #${booking.id} was cancelled and remains in your history.`
      } catch (error) {
        bookingError.value = error.message
      } finally {
        bookingLoading.value = false
      }
    }

    const deleteBooking = async (booking) => {
      if (!window.confirm(`Delete test booking #${booking.id}? This cannot be undone.`)) return
      bookingLoading.value = true
      bookingError.value = ''
      confirmation.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/bookings/${booking.id}`, { method: 'DELETE' })
        if (!response.ok) throw new Error(await getErrorMessage(response, 'Booking could not be deleted.'))
        bookings.value = bookings.value.filter((item) => item.id !== booking.id)
        confirmation.value = `Test booking #${booking.id} was deleted.`
      } catch (error) {
        bookingError.value = error.message
      } finally {
        bookingLoading.value = false
      }
    }

    onMounted(loadBookings)

    return {
      bookingError,
      bookingForm,
      bookingLoading,
      bookings,
      cancelBooking,
      confirmation,
      deleteBooking,
      flattenedStays,
      formatDate,
      formatMoney,
      loadBookings,
      query,
      search,
      searchError,
      searchResults,
      searched,
      searching,
      selectStay,
      selectedStay,
      submitBooking,
    }
  },
  template: `
    <main class="shell">
      <header class="hero">
        <div>
          <p class="eyebrow">LOCAL TRAVEL DEMO</p>
          <h1>Wayfarer Lite</h1>
          <p class="lede">Find a stay, make a simulated booking, and manage your trip history.</p>
        </div>
        <p class="demo-note">Demo traveler: Alex Morgan</p>
      </header>

      <section class="panel search-panel" aria-labelledby="search-heading">
        <div class="section-heading">
          <div>
            <p class="eyebrow">1. SEARCH</p>
            <h2 id="search-heading">Find a hotel</h2>
          </div>
          <p>Try <strong>Harborview</strong>, <strong>Desert</strong>, or <strong>Maple</strong>.</p>
        </div>
        <form class="search-form" @submit.prevent="search">
          <label for="hotel-search">Hotel name</label>
          <div class="search-controls">
            <input id="hotel-search" v-model="query" type="search" autocomplete="off" placeholder="e.g., Harborview" />
            <button class="primary" type="submit" :disabled="searching">{{ searching ? 'Searching…' : 'Search' }}</button>
          </div>
        </form>
        <p v-if="searchError" class="notice error" role="alert">{{ searchError }}</p>
        <p v-else-if="searched && !searching && searchResults.length === 0" class="notice">No hotels matched “{{ query.trim() }}”. Try another name.</p>

        <div v-if="flattenedStays.length" class="table-wrap" aria-live="polite">
          <table>
            <caption>Matching hotels and available stays</caption>
            <thead>
              <tr>
                <th scope="col">Hotel</th>
                <th scope="col">Location</th>
                <th scope="col">Stay</th>
                <th scope="col">Room</th>
                <th scope="col">Available</th>
                <th scope="col">Nightly rate</th>
                <th scope="col"><span class="sr-only">Book</span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="stay in flattenedStays" :key="stay.id">
                <td>{{ stay.hotel_name }}</td>
                <td>{{ stay.city }}</td>
                <td>{{ formatDate(stay.check_in) }} – {{ formatDate(stay.check_out) }}</td>
                <td>{{ stay.room_type }}</td>
                <td>{{ stay.available_rooms }} rooms</td>
                <td>{{ formatMoney(stay.nightly_rate) }}</td>
                <td><button class="text-button" type="button" :disabled="stay.available_rooms === 0" @click="selectStay(stay)">{{ stay.available_rooms ? 'Book stay' : 'Sold out' }}</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-if="selectedStay" class="panel booking-panel" aria-labelledby="booking-heading">
        <div class="section-heading">
          <div>
            <p class="eyebrow">2. BOOK</p>
            <h2 id="booking-heading">Confirm your simulated stay</h2>
          </div>
          <button class="quiet-button" type="button" @click="selectedStay = null">Close</button>
        </div>
        <p class="selected-stay"><strong>{{ selectedStay.hotel_name }}</strong> · {{ selectedStay.room_type }} · {{ formatDate(selectedStay.check_in) }} – {{ formatDate(selectedStay.check_out) }}</p>
        <form id="booking-form" class="booking-form" @submit.prevent="submitBooking" tabindex="-1">
          <label>
            Traveler
            <select v-model="bookingForm.user_id">
              <option :value="1">Alex Morgan</option>
              <option :value="2">Jordan Lee</option>
            </select>
          </label>
          <label>
            Guest name
            <input v-model.trim="bookingForm.guest_name" required minlength="2" maxlength="100" />
          </label>
          <label>
            Guests
            <input v-model.number="bookingForm.guests" type="number" min="1" max="10" required />
          </label>
          <button class="primary" type="submit" :disabled="bookingLoading">{{ bookingLoading ? 'Saving…' : 'Confirm booking' }}</button>
        </form>
      </section>

      <section class="panel history-panel" aria-labelledby="history-heading">
        <div class="section-heading">
          <div>
            <p class="eyebrow">3. HISTORY</p>
            <h2 id="history-heading">Your bookings</h2>
          </div>
          <button class="quiet-button" type="button" @click="loadBookings" :disabled="bookingLoading">Refresh</button>
        </div>
        <p v-if="confirmation" class="notice success" role="status">{{ confirmation }}</p>
        <p v-if="bookingError" class="notice error" role="alert">{{ bookingError }}</p>
        <p v-if="bookingLoading && !bookings.length" class="notice">Loading bookings…</p>
        <p v-else-if="!bookings.length" class="notice">No bookings yet. Search for a hotel to create one.</p>
        <ol v-else class="booking-list">
          <li v-for="booking in bookings" :key="booking.id" class="booking-card">
            <div>
              <div class="booking-title-row">
                <h3>{{ booking.hotel_name }}</h3>
                <span class="status" :class="booking.status">{{ booking.status }}</span>
              </div>
              <p>{{ booking.room_type }} · {{ booking.city }} · {{ formatDate(booking.check_in) }} – {{ formatDate(booking.check_out) }}</p>
              <p class="booking-meta">Booking #{{ booking.id }} · {{ booking.guests }} guest<span v-if="booking.guests !== 1">s</span> · {{ formatMoney(booking.total_price) }}</p>
            </div>
            <div class="booking-actions">
              <button v-if="booking.status === 'confirmed'" class="secondary" type="button" :disabled="bookingLoading" @click="cancelBooking(booking)">Cancel booking</button>
              <button class="danger" type="button" :disabled="bookingLoading" @click="deleteBooking(booking)">Delete test booking</button>
            </div>
          </li>
        </ol>
      </section>
    </main>
  `,
}

createApp(App).mount('#app')
