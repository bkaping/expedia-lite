import { computed, createApp, onBeforeUnmount, onMounted, ref } from 'vue'
import './style.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const EMPTY_PROFILE = () => ({ display_name: null, cue_style: null, practice_aim: null, updated_at: null })
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
    const history = ref({ usual_skill_id: null, completed_practice_count: 0, profile: EMPTY_PROFILE(), sessions: [], messages: [] })
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
    const profileDraft = ref({ display_name: '', cue_style: '', practice_aim: '' })
    const profileLoading = ref(false)
    const profileStatus = ref('')

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
    const profile = computed(() => history.value.profile ?? EMPTY_PROFILE())
    const profileName = computed(() => profile.value.display_name || '')
    const completedCount = computed(() => history.value.completed_practice_count ?? 0)
    const cueCopy = computed(() => {
      if (profile.value.cue_style === 'brief') return 'Your selected cue style is brief: you will see a simple count and the pause/end controls.'
      if (profile.value.cue_style === 'step_by_step') return 'Your selected cue style is step-by-step: the practice labels every four-count inhale and six-count exhale.'
      return 'The practice uses a visual count with clear pause and end controls.'
    })
    const aimCopy = computed(() => {
      if (profile.value.practice_aim === 'one_short_practice') return 'Your selected aim is one short practice.'
      if (profile.value.practice_aim === 'review_pattern') return 'Your selected aim is to review the 4-in / 6-out pattern.'
      return ''
    })

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

    const copyProfileToDraft = (savedProfile = profile.value) => {
      profileDraft.value = {
        display_name: savedProfile.display_name ?? '',
        cue_style: savedProfile.cue_style ?? '',
        practice_aim: savedProfile.practice_aim ?? '',
      }
    }

    const showProfile = async () => {
      problem.value = ''
      profileStatus.value = ''
      if (currentSession.value?.outcome === 'active') {
        const stopped = await leavePractice()
        if (!stopped) return
      }
      copyProfileToDraft()
      screen.value = 'profile'
    }

    const saveProfile = async () => {
      profileLoading.value = true
      profileStatus.value = ''
      problem.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/profile`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            display_name: profileDraft.value.display_name.trim() || null,
            cue_style: profileDraft.value.cue_style || null,
            practice_aim: profileDraft.value.practice_aim || null,
          }),
        })
        if (!response.ok) throw new Error(await errorMessage(response))
        const savedProfile = await response.json()
        history.value = { ...history.value, profile: savedProfile }
        copyProfileToDraft(savedProfile)
        profileStatus.value = 'Profile saved locally. You can change or reset these choices at any time.'
      } catch (error) {
        problem.value = error.message || 'The profile could not be saved.'
      } finally {
        profileLoading.value = false
      }
    }

    const resetProfile = async () => {
      profileLoading.value = true
      profileStatus.value = ''
      problem.value = ''
      try {
        const response = await fetch(`${API_BASE_URL}/api/profile`, { method: 'DELETE' })
        if (!response.ok) throw new Error(await errorMessage(response))
        const clearedProfile = await response.json()
        history.value = { ...history.value, profile: clearedProfile }
        copyProfileToDraft(clearedProfile)
        profileStatus.value = 'Profile reset. The standard interface is now shown.'
      } catch (error) {
        problem.value = error.message || 'The profile could not be reset.'
      } finally {
        profileLoading.value = false
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
        problem.value = 'Enter a short fictional message, or leave this optional step.'
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
        problem.value = error.message || 'The optional coursework chatbot is unavailable. The practice is still saved.'
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
      aimCopy,
      beginSession,
      breathElapsed,
      breathRunning,
      completedCount,
      crisisOpen,
      cueCopy,
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
      profile,
      profileDraft,
      profileLoading,
      profileName,
      profileStatus,
      reflectionLoading,
      reflectionResult,
      reflectionText,
      remaining,
      resumeBreathing,
      screen,
      saveProfile,
      sendReflection,
      showHistory,
      showProfile,
      stage,
      startBreathing,
      resetProfile,
    }
  },
  template: `
    <main class="app-shell">
      <button class="crisis-button" type="button" @click="crisisOpen = true">Crisis support</button>

      <header class="site-header">
        <button class="wordmark" type="button" @click="goHome">stillpoint</button>
        <nav aria-label="Primary navigation">
          <button :aria-current="screen === 'home' ? 'page' : undefined" type="button" @click="goHome">Practice</button>
          <button :aria-current="screen === 'profile' ? 'page' : undefined" type="button" @click="showProfile">My profile</button>
          <button :aria-current="screen === 'history' ? 'page' : undefined" type="button" @click="showHistory">Saved history</button>
        </nav>
      </header>

      <section v-if="screen === 'home'" class="home-view" aria-labelledby="home-heading">
        <p class="eyebrow">COURSEWORK SKILLS PROTOTYPE</p>
        <h1 id="home-heading">{{ profileName ? 'Welcome, ' + profileName + '.' : 'One small practice.' }}</h1>
        <p class="lede">For fictional class scenarios only. This is not therapy, diagnosis, crisis care, or a service to rely on during distress.</p>
        <p v-if="problem" class="notice problem" role="alert">{{ problem }}</p>
        <section class="adaptation-card" aria-labelledby="adaptation-heading">
          <div>
            <p class="eyebrow">YOUR OPTIONAL SETUP</p>
            <h2 id="adaptation-heading">The interface follows choices you control.</h2>
            <p>{{ cueCopy }}</p>
            <p v-if="aimCopy">{{ aimCopy }}</p>
            <p v-if="completedCount" class="quiet-copy">Saved history: {{ completedCount }} completed practice{{ completedCount === 1 ? '' : 's' }}. The repeat shortcut below is optional.</p>
          </div>
          <button class="quiet-button" type="button" @click="showProfile">{{ profileName || profile.cue_style || profile.practice_aim ? 'Edit profile' : 'Set optional profile' }}</button>
        </section>
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
            <p class="eyebrow">OPTIONAL COURSEWORK CHATBOT</p>
            <label for="fictional-note">Send a fictional message after this completed practice</label>
            <textarea id="fictional-note" v-model="reflectionText" maxlength="320" placeholder="Example: I followed the fictional count."></textarea>
            <p class="quiet-copy">The chatbot receives this fictional message plus your explicit profile choices and completed-practice count. It can only return one short acknowledgment. It cannot change this practice or provide therapeutic advice.</p>
            <button class="quiet-button" type="submit" :disabled="reflectionLoading">{{ reflectionLoading ? 'Sending…' : 'Send to coursework chatbot' }}</button>
          </form>
          <p v-if="reflectionResult" class="notice" :class="{ warning: reflectionResult.mode === 'safety_route' }" aria-live="polite"><strong>{{ reflectionResult.mode === 'reply' ? 'Coursework chatbot' : 'Safety handling' }}:</strong> {{ reflectionResult.message }}</p>
          <button class="primary" type="button" @click="goHome">Choose a practice</button>
        </section>
      </section>

      <section v-else-if="screen === 'profile'" class="profile-view" aria-labelledby="profile-heading">
        <p class="eyebrow">OPTIONAL LOCAL PROFILE</p>
        <h1 id="profile-heading">Set the interface you want.</h1>
        <p class="lede">These are fictional-coursework preferences, not a health assessment. Leave them blank for the standard interface. You can edit or reset them at any time.</p>
        <p v-if="problem" class="notice problem" role="alert">{{ problem }}</p>
        <p v-if="profileStatus" class="notice" role="status">{{ profileStatus }}</p>
        <form class="profile-card" @submit.prevent="saveProfile">
          <label for="display-name">Optional display name or nickname</label>
          <input id="display-name" v-model="profileDraft.display_name" maxlength="24" autocomplete="nickname" placeholder="Example: Avery">
          <fieldset>
            <legend>Preferred cue style</legend>
            <label><input v-model="profileDraft.cue_style" type="radio" value=""> Standard interface</label>
            <label><input v-model="profileDraft.cue_style" type="radio" value="brief"> Brief visual count</label>
            <label><input v-model="profileDraft.cue_style" type="radio" value="step_by_step"> Step-by-step labels</label>
          </fieldset>
          <fieldset>
            <legend>Optional practice aim</legend>
            <label><input v-model="profileDraft.practice_aim" type="radio" value=""> No selected aim</label>
            <label><input v-model="profileDraft.practice_aim" type="radio" value="one_short_practice"> Complete one short practice</label>
            <label><input v-model="profileDraft.practice_aim" type="radio" value="review_pattern"> Review the 4-in / 6-out pattern</label>
          </fieldset>
          <p class="quiet-copy">Saved locally: only this nickname, selected cue style, and selected practice aim. The activity history separately stores neutral timing/outcome records and optional fictional chatbot messages.</p>
          <div class="profile-actions"><button class="primary" type="submit" :disabled="profileLoading">{{ profileLoading ? 'Saving…' : 'Save profile' }}</button><button class="quiet-button" type="button" :disabled="profileLoading" @click="resetProfile">Reset to defaults</button></div>
        </form>
        <section class="profile-context" aria-labelledby="usage-heading">
          <h2 id="usage-heading">What the app adapts</h2>
          <p>It changes the greeting and cue explanation from your saved choices. It may offer your latest completed skill as an optional repeat shortcut. The coursework chatbot receives only your explicit profile choices and the count of completed practices—not a diagnosis, score, or inferred emotional state.</p>
        </section>
      </section>

      <section v-else class="history-view" aria-labelledby="history-heading">
        <p class="eyebrow">LOCAL SQLITE RECORD</p>
        <h1 id="history-heading">Saved practice history</h1>
        <p class="lede">This local review shows recent practice sessions and optional fictional chatbot messages. It does not score or diagnose you.</p>
        <button class="quiet-button refresh-button" type="button" :disabled="loadingHistory" @click="showHistory">{{ loadingHistory ? 'Refreshing…' : 'Refresh history' }}</button>
        <p v-if="problem" class="notice problem" role="alert">{{ problem }}</p>
        <section class="history-section" aria-labelledby="sessions-heading">
          <h2 id="sessions-heading">Practice sessions</h2>
          <p v-if="!history.sessions.length" class="empty-copy">No sessions are saved yet.</p>
          <ol v-else class="history-list">
            <li v-for="session in history.sessions" :key="session.id"><article class="history-card"><div><strong>Paced breathing (4–6)</strong><span>{{ formatDate(session.started_at) }} · {{ session.active_seconds ?? 0 }} active seconds · {{ session.source === 'usual_skill' ? 'optional repeat' : 'chosen' }}</span></div><span class="outcome" :class="session.outcome">{{ session.outcome }}</span></article></li>
          </ol>
        </section>
        <section class="history-section" aria-labelledby="notes-heading">
          <h2 id="notes-heading">Optional chatbot messages</h2>
          <p v-if="!history.messages.length" class="empty-copy">No optional fictional chatbot messages are saved yet.</p>
          <ol v-else class="message-list">
            <li v-for="message in history.messages" :key="message.id"><article class="message-card" :class="message.role"><strong>{{ message.role === 'assistant' ? 'Coursework chatbot' : message.role === 'system' ? 'Safety handling' : 'Fictional message' }}</strong><p>{{ message.body }}</p></article></li>
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
