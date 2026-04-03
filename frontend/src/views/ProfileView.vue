<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config/api'

const router = useRouter()
const user = ref(null)
const mentorProfile = ref(null)
const languages = ref([])
const learningLanguageId = ref('')
const offeredLanguageId = ref('')
const requestedLanguageId = ref('')
const availabilityDetails = ref('')
const exchangeTerms = ref('')
const saveLoading = ref(false)
const saveMessage = ref('')
const loading = ref(false)
const error = ref('')
const progressLoading = ref(false)
const progressError = ref('')
const progressEntries = ref([])
const progressLanguageFilter = ref('all')

const getToken = () => localStorage.getItem('token') || localStorage.getItem('access_token')

const getAvailableRequestedLanguages = () => {
  if (!offeredLanguageId.value) {
    return languages.value
  }
  return languages.value.filter((lang) => String(lang.id) !== String(offeredLanguageId.value))
}

const availableProgressLanguages = computed(() => {
  const unique = new Map()
  progressEntries.value.forEach((entry) => {
    if (!entry.languageId) {
      return
    }
    unique.set(String(entry.languageId), entry.languageName)
  })
  return Array.from(unique.entries()).map(([id, name]) => ({ id, name }))
})

const filteredProgressEntries = computed(() => {
  if (progressLanguageFilter.value === 'all') {
    return progressEntries.value
  }

  return progressEntries.value.filter(
    (entry) => String(entry.languageId) === String(progressLanguageFilter.value)
  )
})

const filteredProgressStats = computed(() => {
  const entries = filteredProgressEntries.value
  const completedSessions = entries.filter((entry) => entry.session.status === 'completed').length
  const ratedEntries = entries.filter((entry) => typeof entry.progress?.rating === 'number')
  const averageRating = ratedEntries.length
    ? (ratedEntries.reduce((sum, entry) => sum + entry.progress.rating, 0) / ratedEntries.length).toFixed(1)
    : null

  return {
    totalSessions: entries.length,
    completedSessions,
    ratedSessions: ratedEntries.length,
    averageRating,
  }
})

const buildProgressState = (sessionsData, progressLogsData, mentorProfilesData, evaluationsBySessionId = new Map()) => {
  const progressBySessionId = new Map(progressLogsData.map((log) => [log.session_id, log]))
  const mentorProfileById = new Map(mentorProfilesData.map((profile) => [profile.id, profile]))
  const languageNameById = new Map(languages.value.map((lang) => [lang.id, lang.name]))

  const entries = sessionsData
    .map((session) => ({
      session,
      progress: progressBySessionId.get(session.id) || evaluationsBySessionId.get(session.id) || null,
      languageId: mentorProfileById.get(session.mentor_profile_id)?.offered_language_id ?? null,
      languageName: languageNameById.get(mentorProfileById.get(session.mentor_profile_id)?.offered_language_id) || 'Nincs megadva',
    }))
    .sort((a, b) => new Date(b.session.scheduled_time).getTime() - new Date(a.session.scheduled_time).getTime())

  progressEntries.value = entries
}

const fetchProgressOverview = async (token) => {
  progressLoading.value = true
  progressError.value = ''

  try {
    const [sessionsResponse, mentorProfilesResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/sessions`, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      }),
      fetch(`${API_BASE_URL}/mentor-profiles`, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      }),
    ])

    if (!sessionsResponse.ok || !mentorProfilesResponse.ok) {
      throw new Error('Nem sikerült betölteni az előrehaladás adatait.')
    }

    const [sessionsData, mentorProfilesData] = await Promise.all([sessionsResponse.json(), mentorProfilesResponse.json()])

    let progressLogsData = []
    try {
      const logsResponse = await fetch(`${API_BASE_URL}/progress-logs`, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      })
      if (logsResponse.ok) {
        progressLogsData = await logsResponse.json()
      }
    } catch {
      progressLogsData = []
    }

    const evaluationResults = await Promise.all(
      sessionsData.map(async (session) => {
        try {
          const response = await fetch(`${API_BASE_URL}/sessions/${session.id}/evaluations`, {
            headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
          })
          if (!response.ok) {
            return [session.id, null]
          }

          const evaluations = await response.json()
          const currentStudentEvaluation = evaluations.find(
            (evaluation) => String(evaluation.student_id) === String(user.value?.id)
          )
          return [session.id, currentStudentEvaluation || evaluations?.[0] || null]
        } catch {
          return [session.id, null]
        }
      })
    )

    const evaluationsBySessionId = new Map(evaluationResults)

    buildProgressState(sessionsData, progressLogsData, mentorProfilesData, evaluationsBySessionId)
  } catch (err) {
    progressError.value = err.message || 'Hiba történt az előrehaladás betöltésekor.'
  } finally {
    progressLoading.value = false
  }
}

const fetchCurrentUser = async () => {
  loading.value = true
  error.value = ''
  saveMessage.value = ''

  try {
    const token = getToken()
    if (!token) {
      router.push({ name: 'Login' })
      return
    }

    const [meResponse, languagesResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/users/me`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      }),
      fetch(`${API_BASE_URL}/languages`),
    ])

    if (!meResponse.ok) throw new Error('Nem sikerült lekérni a profilt.')
    if (!languagesResponse.ok) throw new Error('Nem sikerult lekerdezni a nyelveket.')

    const meData = await meResponse.json()
    languages.value = await languagesResponse.json()
    user.value = meData
    learningLanguageId.value = meData.learning_language_id ? String(meData.learning_language_id) : ''

    if (meData.role === 'student') {
      await fetchProgressOverview(token)
    } else {
      progressEntries.value = []
      progressError.value = ''
      progressLoading.value = false
    }

    if (meData.role === 'mentor') {
      const mentorProfileResponse = await fetch(`${API_BASE_URL}/mentor-profile/me`, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      })

      if (!mentorProfileResponse.ok) throw new Error('Nem sikerult a mentor profil adatait lekerdezni.')

      const mentorData = await mentorProfileResponse.json()
      mentorProfile.value = mentorData
      offeredLanguageId.value = mentorData.offered_language_id ? String(mentorData.offered_language_id) : ''
      requestedLanguageId.value = mentorData.requested_language_id ? String(mentorData.requested_language_id) : ''
      availabilityDetails.value = mentorData.availability_details || ''
      exchangeTerms.value = mentorData.exchange_terms || ''
    }
  } catch (err) {
    error.value = err.message || 'Hiba történt.'
  } finally {
    loading.value = false
  }
}

const updateMentorLanguages = async () => {
  if (!user.value || user.value.role !== 'mentor') return

  if (offeredLanguageId.value && requestedLanguageId.value) {
    if (Number(offeredLanguageId.value) === Number(requestedLanguageId.value)) {
      saveMessage.value = 'A tanított és tanult nyelvek nem lehetnek azonosak!'
      return
    }
  }

  saveMessage.value = ''
  saveLoading.value = true
  try {
    const token = getToken()
    if (!token) { router.push({ name: 'Login' }); return }

    const response = await fetch(`${API_BASE_URL}/mentor-profile/me`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        offered_language_id: offeredLanguageId.value ? Number(offeredLanguageId.value) : null,
        requested_language_id: requestedLanguageId.value ? Number(requestedLanguageId.value) : null,
        availability_details: availabilityDetails.value?.trim() || null,
        exchange_terms: exchangeTerms.value?.trim() || null,
      }),
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Nem sikerult menteni a mentor beallitasokat.')
    }

    mentorProfile.value = await response.json()
    saveMessage.value = 'A mentor nyelvi beallitasok sikeresen frissultek.'
  } catch (err) {
    saveMessage.value = err.message || 'Hiba tortent mentes kozben.'
  } finally {
    saveLoading.value = false
  }
}

const updateStudentGoal = async () => {
  if (!user.value || user.value.role !== 'student') return

  if (!learningLanguageId.value) {
    saveMessage.value = 'Kérlek, válassz egy tanulni kívánt nyelvet.'
    return
  }

  saveMessage.value = ''
  saveLoading.value = true
  try {
    const token = getToken()
    if (!token) { router.push({ name: 'Login' }); return }

    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'PUT',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ learning_language_id: Number(learningLanguageId.value) }),
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Nem sikerült menteni a tanulási célt.')
    }

    const data = await response.json()
    user.value = { ...user.value, learning_language_id: data.learning_language_id }
    saveMessage.value = 'A tanulási cél sikeresen frissült.'
  } catch (err) {
    saveMessage.value = err.message || 'Hiba történt mentés közben.'
  } finally {
    saveLoading.value = false
  }
}

onMounted(() => {
  fetchCurrentUser()
})
</script>

<template>
  <div class="profile">
    <div class="profile-shell">
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="loading" class="loading">Betöltés...</div>

      <div v-if="user" class="profile-card">
        <div class="card-header">
          <div class="avatar">{{ user.name?.charAt(0)?.toUpperCase() }}</div>
          <div class="card-header-info">
            <h2>{{ user.name }}</h2>
            <p class="email">{{ user.email }}</p>
            <span class="role-badge" :class="user.role">{{ user.role }}</span>
          </div>
        </div>

        <form v-if="user.role === 'student'" class="profile-form" @submit.prevent="updateStudentGoal">
          <h3>Tanulási cél</h3>

          <div class="field-group">
            <label for="learningLanguage">Tanulni kívánt nyelv</label>
            <select id="learningLanguage" v-model="learningLanguageId" class="input">
              <option value="">Válassz nyelvet</option>
              <option v-for="language in languages" :key="`student-${language.id}`" :value="String(language.id)">
                {{ language.name }}
              </option>
            </select>
          </div>

          <button type="submit" class="btn-primary" :disabled="saveLoading">
            {{ saveLoading ? 'Mentés...' : 'Tanulási cél mentése' }}
          </button>
          <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>
        </form>

        <form v-if="user.role === 'mentor'" class="profile-form" @submit.prevent="updateMentorLanguages">
          <h3>Mentor nyelvi beállítások</h3>

          <div class="field-group">
            <label for="offeredLanguage">Tanított nyelv</label>
            <select id="offeredLanguage" v-model="offeredLanguageId" class="input">
              <option value="">Válassz nyelvet</option>
              <option v-for="language in languages" :key="language.id" :value="String(language.id)">
                {{ language.name }}
              </option>
            </select>
          </div>

          <div class="field-group">
            <label for="requestedLanguage">Tanulni vágyott nyelv</label>
            <select id="requestedLanguage" v-model="requestedLanguageId" class="input">
              <option value="">Válassz nyelvet</option>
              <option v-for="language in getAvailableRequestedLanguages()" :key="`request-${language.id}`" :value="String(language.id)">
                {{ language.name }}
              </option>
            </select>
          </div>

          <div class="field-group">
            <label for="availabilityDetails">Elérhetőség</label>
            <textarea
              id="availabilityDetails"
              v-model="availabilityDetails"
              class="input"
              rows="3"
              placeholder="Pl.: Hétköznap esténként 18:00 után"
            />
          </div>

          <div class="field-group">
            <label for="exchangeTerms">Csere feltételei</label>
            <textarea
              id="exchangeTerms"
              v-model="exchangeTerms"
              class="input"
              rows="3"
              placeholder="Pl.: EN-HU nyelvpár, heti minimum 1 alkalom"
            />
          </div>

          <button type="submit" class="btn-primary" :disabled="saveLoading">
            {{ saveLoading ? 'Mentés...' : 'Mentor nyelvek mentése' }}
          </button>
          <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>
        </form>

        <section v-if="user.role === 'student'" class="progress-section">
          <h3>Előrehaladás</h3>

          <div v-if="progressError" class="progress-error">{{ progressError }}</div>
          <div v-else-if="progressLoading" class="loading">Előrehaladás betöltése...</div>
          <div v-else>
            <div class="progress-stats">
              <div class="stat-card">
                <span class="stat-label">Foglalkozások</span>
                <strong>{{ filteredProgressStats.totalSessions }}</strong>
              </div>
              <div class="stat-card">
                <span class="stat-label">Befejezve</span>
                <strong>{{ filteredProgressStats.completedSessions }}</strong>
              </div>
              <div class="stat-card">
                <span class="stat-label">Értékelések</span>
                <strong>{{ filteredProgressStats.ratedSessions }}</strong>
              </div>
              <div class="stat-card">
                <span class="stat-label">Átlag</span>
                <strong>{{ filteredProgressStats.averageRating ? `${filteredProgressStats.averageRating}/5` : '–' }}</strong>
              </div>
            </div>

            <div class="field-group">
              <label for="progressLanguageFilter">Szűrés tanult nyelv szerint</label>
              <select id="progressLanguageFilter" v-model="progressLanguageFilter" class="input">
                <option value="all">Minden tanult nyelv</option>
                <option v-for="language in availableProgressLanguages" :key="`progress-${language.id}`" :value="language.id">
                  {{ language.name }}
                </option>
              </select>
            </div>

            <p v-if="filteredProgressEntries.length === 0" class="progress-empty">Még nincs megjeleníthető előrehaladási adat.</p>

            <div v-else class="progress-list">
              <article v-for="entry in filteredProgressEntries" :key="entry.session.id" class="progress-item">
                <p><strong>Tanult nyelv:</strong> {{ entry.languageName }}</p>
                <p><strong>Időpont:</strong> {{ new Date(entry.session.scheduled_time).toLocaleString('hu-HU') }}</p>
                <p><strong>Státusz:</strong> {{ entry.session.status }}</p>
                <p><strong>Értékelés:</strong> {{ entry.progress?.rating ? `${entry.progress.rating}/5` : 'Nincs értékelés' }}</p>
                <p v-if="entry.progress?.notes"><strong>Megjegyzés:</strong> {{ entry.progress.notes }}</p>
              </article>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile {
  padding: 40px 20px;
  display: flex;
  justify-content: center;
}

.profile-shell {
  width: 100%;
  max-width: 540px;
}

.error {
  color: #b42318;
  background: #fef2f2;
  border: 1px solid #fecaca;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.92rem;
}

.loading {
  color: #666;
  text-align: center;
  padding: 40px;
}

/* Main card */
.profile-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* Card header with avatar */
.card-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  padding-bottom: 22px;
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1f67c8, #3b86e8);
  color: white;
  font-size: 1.4rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-header-info h2 {
  margin: 0 0 2px;
  font-size: 1.15rem;
  color: #f1f5f9;
}

.card-header-info .email {
  margin: 0 0 6px;
  font-size: 0.85rem;
  color: #cbd5e1;
}

.role-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.role-badge.mentor { background: rgba(99, 102, 241, 0.25); color: #818cf8; }
.role-badge.student { background: rgba(34, 197, 94, 0.25); color: #86efac; }

/* Form sections */
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.profile-form h3 {
  margin: 0 0 4px;
  font-size: 1rem;
  color: #f1f5f9;
  font-weight: 700;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.field-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #cbd5e1;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.input {
  padding: 9px 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  font-size: 0.93rem;
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.06);
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.7);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  background: rgba(255, 255, 255, 0.09);
}

textarea.input {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.btn-primary {
  padding: 10px 16px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.92rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s, box-shadow 0.2s;
  margin-top: 4px;
}
.btn-primary:hover { opacity: 0.88; box-shadow: 0 3px 10px rgba(99, 102, 241, 0.3); }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }

.save-message {
  margin: 0;
  color: #86efac;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.88rem;
}

/* Progress section */
.progress-section {
  margin-top: 28px;
  padding-top: 22px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.progress-section h3 {
  margin: 0 0 14px;
  font-size: 1rem;
  color: #f1f5f9;
  font-weight: 700;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}

.stat-card {
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 10px;
  padding: 12px 14px;
  background: rgba(99, 102, 241, 0.08);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  color: #cbd5e1;
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.stat-card strong {
  font-size: 1.4rem;
  color: #f1f5f9;
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.progress-item {
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 10px;
  padding: 12px 14px;
  background: rgba(99, 102, 241, 0.08);
}

.progress-item p {
  margin: 5px 0;
  font-size: 0.9rem;
  color: #cbd5e1;
}

.progress-empty {
  color: #cbd5e1;
  font-size: 0.9rem;
  margin: 10px 0 0;
}

.progress-error {
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 0.9rem;
}
</style>