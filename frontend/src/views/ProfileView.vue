<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

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

const API_BASE_URL = 'http://127.0.0.1:8000'

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

const buildProgressState = (sessionsData, progressLogsData, mentorProfilesData) => {
  const progressBySessionId = new Map(progressLogsData.map((log) => [log.session_id, log]))
  const mentorProfileById = new Map(mentorProfilesData.map((profile) => [profile.id, profile]))
  const languageNameById = new Map(languages.value.map((lang) => [lang.id, lang.name]))

  const entries = sessionsData
    .map((session) => ({
      session,
      progress: progressBySessionId.get(session.id) || null,
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
    const [sessionsResponse, logsResponse, mentorProfilesResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/sessions`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }),
      fetch(`${API_BASE_URL}/progress-logs`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }),
      fetch(`${API_BASE_URL}/mentor-profiles`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }),
    ])

    if (!sessionsResponse.ok || !logsResponse.ok || !mentorProfilesResponse.ok) {
      throw new Error('Nem sikerült betölteni az előrehaladás adatait.')
    }

    const [sessionsData, progressLogsData, mentorProfilesData] = await Promise.all([
      sessionsResponse.json(),
      logsResponse.json(),
      mentorProfilesResponse.json(),
    ])

    buildProgressState(sessionsData, progressLogsData, mentorProfilesData)
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
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }),
      fetch(`${API_BASE_URL}/languages`),
    ])

    if (!meResponse.ok) {
      throw new Error('Nem sikerült lekérni a profilt.')
    }

    if (!languagesResponse.ok) {
      throw new Error('Nem sikerult lekerdezni a nyelveket.')
    }

    const meData = await meResponse.json()
    languages.value = await languagesResponse.json()
    user.value = meData
    learningLanguageId.value = meData.learning_language_id ? String(meData.learning_language_id) : ''

    await fetchProgressOverview(token)

    if (meData.role === 'mentor') {
      const mentorProfileResponse = await fetch(`${API_BASE_URL}/mentor-profile/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!mentorProfileResponse.ok) {
        throw new Error('Nem sikerult a mentor profil adatait lekerdezni.')
      }

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
  if (!user.value || user.value.role !== 'mentor') {
    return
  }

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
    if (!token) {
      router.push({ name: 'Login' })
      return
    }

    const response = await fetch(`${API_BASE_URL}/mentor-profile/me`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
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

    const data = await response.json()
    mentorProfile.value = data
    saveMessage.value = 'A mentor nyelvi beallitasok sikeresen frissultek.'
  } catch (err) {
    saveMessage.value = err.message || 'Hiba tortent mentes kozben.'
  } finally {
    saveLoading.value = false
  }
}

const updateStudentGoal = async () => {
  if (!user.value || user.value.role !== 'student') {
    return
  }

  if (!learningLanguageId.value) {
    saveMessage.value = 'Kérlek, válassz egy tanulni kívánt nyelvet.'
    return
  }

  saveMessage.value = ''
  saveLoading.value = true
  try {
    const token = getToken()
    if (!token) {
      router.push({ name: 'Login' })
      return
    }

    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        learning_language_id: Number(learningLanguageId.value),
      }),
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
      <h2>Profil</h2>

      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="loading" class="loading">Betöltés...</div>

      <div v-if="user" class="profile-info">
        <p><strong>Név:</strong> {{ user.name }}</p>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><strong>Szerep:</strong> {{ user.role }}</p>

        <form v-if="user.role === 'student'" class="mentor-form" @submit.prevent="updateStudentGoal">
          <h3>Tanulási cél</h3>

          <label for="learningLanguage">Tanulni kívánt nyelv</label>
          <select id="learningLanguage" v-model="learningLanguageId">
            <option value="">Valassz nyelvet</option>
            <option v-for="language in languages" :key="`student-${language.id}`" :value="String(language.id)">
              {{ language.name }}
            </option>
          </select>

          <button type="submit" :disabled="saveLoading">
            {{ saveLoading ? 'Mentes...' : 'Tanulási cél mentése' }}
          </button>

          <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>
        </form>

        <form v-if="user.role === 'mentor'" class="mentor-form" @submit.prevent="updateMentorLanguages">
          <h3>Mentor nyelvi beallitasok</h3>

          <label for="offeredLanguage">Tanított nyelv</label>
          <select id="offeredLanguage" v-model="offeredLanguageId">
            <option value="">Valassz nyelvet</option>
            <option v-for="language in languages" :key="language.id" :value="String(language.id)">
              {{ language.name }}
            </option>
          </select>

          <label for="requestedLanguage">Tanulni vágyott nyelv</label>
          <select id="requestedLanguage" v-model="requestedLanguageId">
            <option value="">Valassz nyelvet</option>
            <option v-for="language in getAvailableRequestedLanguages()" :key="`request-${language.id}`" :value="String(language.id)">
              {{ language.name }}
            </option>
          </select>

          <label for="availabilityDetails">Elérhetőség</label>
          <textarea
            id="availabilityDetails"
            v-model="availabilityDetails"
            rows="3"
            placeholder="Pl.: Hetkoznap estenkent 18:00 utan"
          />

          <label for="exchangeTerms">Csere feltételei</label>
          <textarea
            id="exchangeTerms"
            v-model="exchangeTerms"
            rows="3"
            placeholder="Pl.: EN-HU nyelvpar, heti minimum 1 alkalom"
          />

          <button type="submit" :disabled="saveLoading">
            {{ saveLoading ? 'Mentes...' : 'Mentor nyelvek mentese' }}
          </button>

          <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>
        </form>

        <section class="progress-section">
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
                <strong>{{ filteredProgressStats.averageRating ? `${filteredProgressStats.averageRating}/5` : '-' }}</strong>
              </div>
            </div>

            <label for="progressLanguageFilter" class="progress-filter-label">Szűrés tanult nyelv szerint</label>
            <select id="progressLanguageFilter" v-model="progressLanguageFilter" class="progress-filter-select">
              <option value="all">Minden tanult nyelv</option>
              <option v-for="language in availableProgressLanguages" :key="`progress-${language.id}`" :value="language.id">
                {{ language.name }}
              </option>
            </select>

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
  padding: 20px;
  display: flex;
  justify-content: center;
}

.profile-shell {
  width: 100%;
  max-width: 640px;
}

.profile h2 {
  color: #2c3e50;
}

.error {
  color: #b42318;
  background: #f8d7da;
  padding: 12px;
  border-radius: 6px;
}

.loading {
  color: #666;
  text-align: center;
  padding: 40px;
}

.profile-info {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  max-width: 500px;
}

.profile-info p {
  margin: 12px 0;
}

.mentor-form {
  margin-top: 20px;
  border-top: 1px solid #e3e3e3;
  padding-top: 16px;
  display: grid;
  gap: 10px;
}

.mentor-form h3 {
  margin: 0 0 6px;
  color: #2c3e50;
}

.mentor-form label {
  font-size: 0.92rem;
  font-weight: 600;
  color: #324a62;
}

.mentor-form select,
.mentor-form textarea,
.mentor-form button {
  border: 1px solid #cfd9e3;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 0.95rem;
}

.mentor-form textarea {
  resize: vertical;
  min-height: 72px;
}

.mentor-form button {
  border: none;
  background: #1f67c8;
  color: white;
  cursor: pointer;
  font-weight: 600;
}

.mentor-form button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.save-message {
  margin: 2px 0 0;
  color: #135d2c;
  font-size: 0.92rem;
}

.progress-section {
  margin-top: 22px;
  border-top: 1px solid #e3e3e3;
  padding-top: 16px;
}

.progress-section h3 {
  margin: 0 0 10px;
  color: #2c3e50;
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.stat-card {
  border: 1px solid #d6e0eb;
  border-radius: 8px;
  padding: 10px 12px;
  background: #f8fbff;
  display: grid;
  gap: 4px;
}

.stat-label {
  color: #516476;
  font-size: 0.85rem;
}

.progress-list {
  display: grid;
  gap: 10px;
}

.progress-filter-label {
  display: block;
  margin: 6px 0;
  font-size: 0.9rem;
  color: #324a62;
  font-weight: 600;
}

.progress-filter-select {
  width: 100%;
  border: 1px solid #cfd9e3;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 0.95rem;
  margin-bottom: 12px;
}

.progress-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px 12px;
  background: #ffffff;
}

.progress-item p {
  margin: 6px 0;
}

.progress-empty {
  color: #5f6e7d;
  margin: 8px 0 0;
}

.progress-error {
  color: #b42318;
  background: #f8d7da;
  padding: 10px 12px;
  border-radius: 6px;
}
</style>
