import { computed, createApp, onBeforeUnmount, onMounted, ref } from 'vue'
import './style.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const SKILL = {
  id: 'paced_breathing',
  title: 'Paced breathing (4–6)',
  summary: 'Breathe in for four counts and out for six, for one minute.',
}

const errorMessage = async (response) => {
  try {
    const payload = await response.json()
    return typeof payload.detail === 'object' ? payload.detail.message : payload.detail
  } catch {
    return 'The application did not return a usable response.'
  }
}

const App = {
  setup() {
    const screen = ref('home')
    const history = ref({ usual_skill_id: null, sessions: [], messages: [] })
    const currentSession = ref(null)
    const stage = ref('ready')
    const loadingHistory = ref(false)
    const problem = ref('')
    const crisisOpen = ref(false)
    const reflectionText = ref('')
    const reflectionResult = ref(null)
    const reflectionLoading = ref(false)
    const breathElapsed = ref(0)
    const breathRunning = ref(false)

    let timerId
    let elapsedMs = 0
    let runningSince = 0

    const remaining = computed(() => Math.max(0, 60 - breathElapsed.value))
    const phase = computed(() => {
      const second = breathElapsed.value % 10
      return second < 4
        ? { text: 'Breathe in', count: 4 - second, direction: 'in' }
        : { text: 'Breathe out', count: 10 - second, direction: 'out' }
    })
    const hasUsualSkill = computed(() => history.value.usual_skill_id === SKILL.id)

    const formatDate = (value) =>
      new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' }).format(
        new Date(value),
      )

    const loadHistory = async () => {
      loadingHistory.value = true
      try {
        const response = await fetch(`${API_BASE_URL}/api/history`)
        if (!response.ok) throw new Error(await errorMessage(response))
        history.value = await response.json()
      } catch (error) {
        problem.value = error.message || 'Saved history could not be loaded.'
      } finally {
        loadingHistory.value = false
      }
    }

    const beginSession = async (source = 'chosen') => {
      problem.value = ''
      reflectionResult.value = null
      try {
        const response = await fetch(`${API_BASE_URL}/api/sessions`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ skill_id: SKILL.id, source }),
        })
        if (!response.ok) throw new Error(await errorMessage(response))
        currentSession.value = await response.json()
        elapsedMs = 0
        breathElapsed.value = 0
        stage.value = 'ready'
        screen.value = 'practice'
      } catch (error) {
        problem.value = error.message || 'The practice could not be started.'
      }
    }

    const stopTimer = () => {
      if (breathRunning.value) elapsedMs += Date.now() - runningSince
      breathRunning.value = false
      window.clearInterval(timerId)
      timerId = undefined
      breathElapsed.value = Math.min(60, Math.floor(elapsedMs / 1000))
    }

    const finishPractice = async (outcome, activeSeconds) => {
      if (!currentSession.value || currentSession.value.outcome !== 'active') return false
      stopTimer()
      problem.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/sessions/${currentSession.value.id}/finish`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ outcome, active_seconds: Math.max(0, Math.round(activeSeconds)) }),
        })
        if (!response.ok) throw new Error(await errorMessage(response))
        currentSession.value = await response.json()
        stage.value = 'finished'
        await loadHistory()
        return true
      } catch (error) {
        problem.value = error.message || 'The practice result could not be saved. You can still use Crisis support or return later.'
        return false
      }
    }

    const updateTimer = () => {
      const totalMs = elapsedMs + (breathRunning.value ? Date.now() - runningSince : 0)
      breathElapsed.value = Math.min(60, Math.floor(totalMs / 1000))
      if (totalMs >= 60_000) {
        stopTimer()
        void finishPractice('completed', 60)
      }
    }

    const startBreathing = () => {
      stage.value = 'active'
      runningSince = Date.now()
      breathRunning.value = true
      timerId = window.setInterval(updateTimer, 200)
      updateTimer()
    }

    const resumeBreathing = () => {
      runningSince = Date.now()
      breathRunning.value = true
      timerId = window.setInterval(updateTimer, 200)
      updateTimer()
    }

    const pauseBreathing = () => stopTimer()

    const leavePractice = () => {
      const activeSeconds = breathElapsed.value
      if (currentSession.value?.outcome === 'active') return finishPractice('stopped', activeSeconds)
      return Promise.resolve(false)
    }

    const goHome = async () => {
      if (currentSession.value?.outcome === 'active') {
        const stopped = await leavePractice()
        if (!stopped) return
      }
      stopTimer()
      screen.value = 'home'
      currentSession.value = null
      stage.value = 'ready'
    }

    const sendReflection = async () => {
      const message = reflectionText.value.trim()
      reflectionResult.value = null
      problem.value = ''
      if (!message) {
        problem.value = 'Enter a short fictional note, or leave this optional step.'
        return
      }
      reflectionLoading.value = true
      try {
        const response = await fetch(`${API_BASE_URL}/api/conversations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: currentSession.value.id, message }),
        })
        if (!response.ok) throw new Error(await errorMessage(response))
        reflectionResult.value = await response.json()
        reflectionText.value = ''
        if (reflectionResult.value.mode === 'safety_route') crisisOpen.value = true
        await loadHistory()
      } catch (error) {
        problem.value = error.message || 'The optional companion is unavailable. The practice is still saved.'
      } finally {
        reflectionLoading.value = false
      }
    }

    const showHistory = async () => {
      problem.value = ''
      if (currentSession.value?.outcome === 'active') {
        const stopped = await leavePractice()
        if (!stopped) return
      }
      screen.value = 'history'
      await loadHistory()
    }

    onMounted(() => { void loadHistory() })
    onBeforeUnmount(() => stopTimer())

    return {
      SKILL,
      beginSession,
      breathElapsed,
      breathRunning,
      crisisOpen,
      currentSession,
      formatDate,
      goHome,
      hasUsualSkill,
      history,
      leavePractice,
      loadingHistory,
      pauseBreathing,
      phase,
      problem,
      reflectionLoading,
      reflectionResult,
      reflectionText,
      remaining,
      resumeBreathing,
      screen,
      sendReflection,
      showHistory,
      stage,
      startBreathing,
    }
  },
  template: `
    <main class="app-shell">
      <button class="crisis-button" type="button" @click="crisisOpen = true">Crisis support</button>

      <header class="site-header">
        <button class="wordmark" type="button" @click="goHome">stillpoint</button>
        <nav aria-label="Primary navigation">
          <button :aria-current="screen === 'home' ? 'page' : undefined" type="button" @click="goHome">Practice</button>
          <button :aria-current="screen === 'history' ? 'page' : undefined" type="button" @click="showHistory">Saved history</button>
        </nav>
      </header>

      <section v-if="screen === 'home'" class="home-view" aria-labelledby="home-heading">
        <p class="eyebrow">COURSEWORK SKILLS PROTOTYPE</p>
        <h1 id="home-heading">One small practice.</h1>
        <p class="lede">For fictional class scenarios only. This is not therapy, diagnosis, crisis care, or a service to rely on during distress.</p>
        <p v-if="problem" class="notice problem" role="alert">{{ problem }}</p>
        <section class="practice-card" aria-labelledby="practice-heading">
          <p class="eyebrow">60 SECONDS INTENDED</p>
          <h2 id="practice-heading">{{ SKILL.title }}</h2>
          <p>{{ SKILL.summary }}</p>
          <p v-if="hasUsualSkill" class="usual-copy">Your most recently completed practice was this one. Choosing it again is optional.</p>
          <button class="primary" type="button" @click="beginSession(hasUsualSkill ? 'usual_skill' : 'chosen')">{{ hasUsualSkill ? 'Use this practice again' : 'Choose this practice' }}</button>
        </section>
        <p class="deferred-note">5–4–3–2–1 sensory grounding remains planned for a later iteration; this Part 3.2 scope implements one complete skill.</p>
      </section>

      <section v-else-if="screen === 'practice' && currentSession" class="practice-view" aria-labelledby="practice-title">
        <p class="eyebrow">ONE STEP AT A TIME</p>
        <h1 id="practice-title">{{ SKILL.title }}</h1>
        <p v-if="problem" class="notice problem" role="alert">{{ problem }}</p>

        <section v-if="stage === 'ready'" class="exercise-card ready-card">
          <p class="instruction">The next screen begins the 60-second practice.</p>
          <p class="quiet-copy">You may pause or leave at any time. Nothing needs to be explained or completed.</p>
          <button class="primary" type="button" @click="startBreathing">Begin practice</button>
          <button class="text-button" type="button" @click="leavePractice">Leave this practice</button>
        </section>

        <section v-else-if="stage === 'active'" class="exercise-card breathing-card" aria-label="Paced breathing exercise">
          <p class="timer-copy">{{ remaining }} seconds remaining</p>
          <div class="breath-orb" :class="'phase-' + phase.direction" aria-hidden="true"><span>{{ phase.count }}</span></div>
          <p class="breath-label" aria-live="polite">{{ phase.text }}</p>
          <p v-if="breathRunning" class="quiet-copy">Follow the count if it feels useful.</p>
          <p v-else class="quiet-copy">The timer is paused. Continue only if you want to.</p>
          <button v-if="breathRunning" class="quiet-button" type="button" @click="pauseBreathing">Pause</button>
          <button v-else class="primary" type="button" @click="resumeBreathing">Continue when ready</button>
          <button class="text-button" type="button" @click="leavePractice">End this practice</button>
        </section>

        <section v-else class="exercise-card finish-card">
          <p class="eyebrow">{{ currentSession.outcome === 'completed' ? 'PRACTICE SAVED' : 'PRACTICE ENDED' }}</p>
          <h2>{{ currentSession.outcome === 'completed' ? 'This practice is marked complete.' : 'You chose to stop. Nothing else is required.' }}</h2>
          <p class="quiet-copy">Active time recorded: {{ currentSession.active_seconds }} seconds.</p>
          <form v-if="currentSession.outcome === 'completed'" class="companion-form" @submit.prevent="sendReflection">
            <label for="fictional-note">Optional fictional note for the course-prototype companion</label>
            <textarea id="fictional-note" v-model="reflectionText" maxlength="320" placeholder="Example: I followed the fictional count."></textarea>
            <p class="quiet-copy">The model can only return one bounded acknowledgment. It cannot change this practice or provide therapeutic advice.</p>
            <button class="quiet-button" type="submit" :disabled="reflectionLoading">{{ reflectionLoading ? 'Sending…' : 'Save note and ask companion' }}</button>
          </form>
          <p v-if="reflectionResult" class="notice" :class="{ warning: reflectionResult.mode === 'safety_route' }">{{ reflectionResult.message }}</p>
          <button class="primary" type="button" @click="goHome">Choose a practice</button>
        </section>
      </section>

      <section v-else class="history-view" aria-labelledby="history-heading">
        <p class="eyebrow">LOCAL SQLITE RECORD</p>
        <h1 id="history-heading">Saved practice history</h1>
        <p class="lede">This local review shows recent practice sessions and optional fictional notes. It does not score or diagnose you.</p>
        <button class="quiet-button refresh-button" type="button" :disabled="loadingHistory" @click="showHistory">{{ loadingHistory ? 'Refreshing…' : 'Refresh history' }}</button>
        <p v-if="problem" class="notice problem" role="alert">{{ problem }}</p>
        <section class="history-section" aria-labelledby="sessions-heading">
          <h2 id="sessions-heading">Practice sessions</h2>
          <p v-if="!history.sessions.length" class="empty-copy">No sessions are saved yet.</p>
          <ol v-else class="history-list">
            <li v-for="session in history.sessions" :key="session.id"><article class="history-card"><div><strong>Paced breathing (4–6)</strong><span>{{ formatDate(session.started_at) }}</span></div><span class="outcome" :class="session.outcome">{{ session.outcome }}</span></article></li>
          </ol>
        </section>
        <section class="history-section" aria-labelledby="notes-heading">
          <h2 id="notes-heading">Optional companion notes</h2>
          <p v-if="!history.messages.length" class="empty-copy">No optional notes are saved yet.</p>
          <ol v-else class="message-list">
            <li v-for="message in history.messages" :key="message.id"><article class="message-card" :class="message.role"><strong>{{ message.role === 'assistant' ? 'Companion' : message.role === 'system' ? 'Safety handling' : 'Fictional note' }}</strong><p>{{ message.body }}</p></article></li>
          </ol>
        </section>
      </section>

      <div v-if="crisisOpen" class="modal-backdrop" @click.self="crisisOpen = false">
        <section class="crisis-modal" role="dialog" aria-modal="true" aria-labelledby="crisis-heading">
          <button class="modal-close" type="button" aria-label="Close crisis support" @click="crisisOpen = false">×</button>
          <p class="eyebrow">CRISIS SUPPORT</p>
          <h2 id="crisis-heading">Get support outside this prototype.</h2>
          <p>If there is immediate danger, seek emergency services now.</p>
          <p>In the United States and its territories, the 988 Suicide &amp; Crisis Lifeline is available by phone, text, or chat.</p>
          <div class="support-links"><a href="tel:988?oai_link_source=model_response_hotline">Call 988</a><a href="sms:988?oai_link_source=model_response_hotline">Text 988</a><a href="https://988lifeline.org/chat/?oai_link_source=model_response_hotline" target="_blank" rel="noreferrer">Chat with 988</a></div>
          <p class="quiet-copy">This panel is already in the browser. It does not rely on a model response, detection result, or the API.</p>
          <button class="primary" type="button" @click="crisisOpen = false">Return to prototype</button>
        </section>
      </div>
    </main>
  `,
}

createApp(App).mount('#app')
