import { createApp, ref } from 'vue'
import './style.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

const App = {
  setup() {
    const query = ref('')
    const results = ref([])
    const searched = ref(false)
    const searching = ref(false)
    const error = ref('')

    const formatMoney = (amount) =>
      new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)

    const search = async () => {
      const hotelName = query.value.trim()
      searched.value = true
      error.value = ''
      results.value = []

      if (!hotelName) {
        error.value = 'Enter a hotel name to search.'
        return
      }

      searching.value = true
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/search?hotel_name=${encodeURIComponent(hotelName)}`,
        )
        if (!response.ok) throw new Error('The hotel search is unavailable. Please try again.')
        results.value = await response.json()
      } catch (requestError) {
        error.value = requestError.message
      } finally {
        searching.value = false
      }
    }

    return { error, formatMoney, query, results, search, searched, searching }
  },
  template: `
    <main class="shell">
      <header class="hero">
        <p class="eyebrow">ASSIGNMENT 1 · PART 1</p>
        <h1>Wayfarer Lite</h1>
        <p class="lede">Search the course hotel list by hotel name.</p>
      </header>

      <section class="panel" aria-labelledby="search-heading">
        <div class="section-heading">
          <div>
            <p class="eyebrow">HOTEL SEARCH</p>
            <h2 id="search-heading">Find a hotel</h2>
          </div>
          <p class="hint">Try <strong>Harbor</strong>, <strong>Maple</strong>, or <strong>Metro</strong>.</p>
        </div>

        <form class="search-form" @submit.prevent="search">
          <label for="hotel-search">Hotel name</label>
          <div class="search-controls">
            <input
              id="hotel-search"
              v-model="query"
              type="search"
              autocomplete="off"
              placeholder="e.g., Harbor Lantern"
            />
            <button class="primary" type="submit" :disabled="searching">
              {{ searching ? 'Searching…' : 'Search' }}
            </button>
          </div>
        </form>

        <p v-if="error" class="notice error" role="alert">{{ error }}</p>
        <p v-else-if="searched && !searching && results.length === 0" class="notice" role="status">
          No hotels matched “{{ query.trim() }}”. Try another hotel name.
        </p>

        <div v-if="results.length" class="table-wrap" aria-live="polite">
          <table>
            <caption>Matching hotels</caption>
            <thead>
              <tr>
                <th scope="col">Hotel</th>
                <th scope="col">City</th>
                <th scope="col">State</th>
                <th scope="col">Nightly rate</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="hotel in results" :key="hotel.hotel_id">
                <td>{{ hotel.hotel_name }}</td>
                <td>{{ hotel.city }}</td>
                <td>{{ hotel.state }}</td>
                <td>{{ formatMoney(hotel.nightly_rate_usd) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </main>
  `,
}

createApp(App).mount('#app')
