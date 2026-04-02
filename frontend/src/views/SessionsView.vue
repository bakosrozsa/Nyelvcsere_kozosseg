<script setup>
import { computed, ref, onMounted } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'
const sessions = ref([])
const mentors = ref([])
const loading = ref(false)
const error = ref('')
const minDateTime = ref('')
const progressBySession = ref({})
const progressForms = ref({})
const progressSaving = ref({})

// Űrlap adatai az új foglaláshoz (Create)
const newSession = ref({
  mentor_profile_id: '',
  scheduled_time: ''
})

const mentorByProfileId = computed(() => {
  const map = new Map()
  mentors.value.forEach((mentor) => {
    map.set(String(mentor.id), mentor)
  })
  return map
})

const getCurrentDateTimeLocal = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

// Biztonságos Axios hívásokhoz a fejléc (token)
const getHeaders = () => {
  const token = localStorage.getItem('token')
  return { Authorization: `Bearer ${token}` }
}

// --- 1. READ (Lekérdezés) ---
const fetchSessions = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.get(`${API_BASE_URL}/sessions`, { headers: getHeaders() })
    sessions.value = response.data
    await fetchProgressLogsForSessions()
  } catch (err) {
    error.value = 'Hiba a foglalkozások lekérésekor.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const fetchProgressLogsForSessions = async () => {
  const nextProgress = {}
  const nextForms = {}

  await Promise.all(
    sessions.value.map(async (session) => {
      try {
        const response = await axios.get(`${API_BASE_URL}/sessions/${session.id}/progress-log`, {
          headers: getHeaders(),
        })
        const progress = response.data
        nextProgress[session.id] = progress
        nextForms[session.id] = {
          notes: progress?.notes || '',
          rating: progress?.rating ? String(progress.rating) : '',
        }
      } catch (err) {
        nextProgress[session.id] = null
        nextForms[session.id] = { notes: '', rating: '' }
      }
    })
  )

  progressBySession.value = nextProgress
  progressForms.value = nextForms
}

const fetchMentors = async () => {
  error.value = ''
  try {
    const headers = getHeaders()
    const [profilesRes, usersRes, languagesRes] = await Promise.all([
      axios.get(`${API_BASE_URL}/mentor-profiles`, { headers }),
      axios.get(`${API_BASE_URL}/users`, { headers }),
      axios.get(`${API_BASE_URL}/languages`, { headers }),
    ])

    const usersById = new Map(usersRes.data.map((u) => [u.id, u]))
    const languagesById = new Map(languagesRes.data.map((l) => [l.id, l]))

    mentors.value = profilesRes.data
      .map((profile) => {
        const user = usersById.get(profile.user_id)
        if (!user) return null
        return {
          id: profile.id,
          name: user.name,
          email: user.email,
          teachesLanguage: languagesById.get(profile.offered_language_id)?.name || 'Nincs megadva',
        }
      })
      .filter(Boolean)

    if (!newSession.value.mentor_profile_id && mentors.value.length > 0) {
      newSession.value.mentor_profile_id = String(mentors.value[0].id)
    }
  } catch (err) {
    error.value = 'Hiba a mentorok lekérésekor.'
    console.error(err)
  }
}

// --- 2. CREATE (Létrehozás) ---
const createSession = async () => {
  if (!newSession.value.scheduled_time || !newSession.value.mentor_profile_id) return

  minDateTime.value = getCurrentDateTimeLocal()
  const selectedDate = new Date(newSession.value.scheduled_time)
  if (Number.isNaN(selectedDate.getTime()) || selectedDate.getTime() < Date.now()) {
    alert('A jelenlegi időpontnál korábbra nem lehet foglalni.')
    return
  }
  
  try {
    // Formázzuk a dátumot a backendnek megfelelő ISO formátumra
    const payload = {
      mentor_profile_id: Number(newSession.value.mentor_profile_id),
      scheduled_time: new Date(newSession.value.scheduled_time).toISOString()
    }
    await axios.post(`${API_BASE_URL}/sessions`, payload, { headers: getHeaders() })
    
    // Sikeres mentés után frissítjük a listát és kiürítjük az űrlapot
    fetchSessions()
    newSession.value.scheduled_time = ''
    alert('Sikeres időpontfoglalás!')
  } catch (err) {
    const apiMessage = err?.response?.data?.detail
    alert(apiMessage || 'Hiba történt a létrehozás során.')
    console.error(err)
  }
}

// --- 3. UPDATE (Módosítás) ---
const updateSessionStatus = async (sessionId, newStatus) => {
  try {
    await axios.put(`${API_BASE_URL}/sessions/${sessionId}`, { status: newStatus }, { headers: getHeaders() })
    fetchSessions() // Frissítjük a listát
  } catch (err) {
    alert('Hiba történt a módosítás során.')
    console.error(err)
  }
}

const canRateSession = (session) => session?.status === 'completed'

// --- 4. DELETE (Törlés) ---
const deleteSession = async (sessionId) => {
  if (!confirm('Biztosan törölni szeretnéd ezt a foglalkozást?')) return

  try {
    await axios.delete(`${API_BASE_URL}/sessions/${sessionId}`, { headers: getHeaders() })
    fetchSessions() // Frissítjük a listát
  } catch (err) {
    alert('Hiba történt a törlés során.')
    console.error(err)
  }
}

const saveSessionProgress = async (session) => {
  const sessionId = session.id
  const form = progressForms.value[sessionId] || { notes: '', rating: '' }
  progressSaving.value = { ...progressSaving.value, [sessionId]: true }

  try {
    const payload = {
      notes: form.notes?.trim() || null,
    }

    if (canRateSession(session)) {
      payload.rating = form.rating ? Number(form.rating) : null
    } else if (form.rating) {
      alert('Értékelést csak befejezett foglalkozáshoz adhatsz meg.')
      return
    }

    const response = await axios.put(
      `${API_BASE_URL}/sessions/${sessionId}/progress-log`,
      payload,
      { headers: getHeaders() }
    )

    progressBySession.value = {
      ...progressBySession.value,
      [sessionId]: response.data,
    }
    alert('Előrehaladás mentve.')
  } catch (err) {
    alert('Hiba történt az előrehaladás mentésekor.')
    console.error(err)
  } finally {
    progressSaving.value = { ...progressSaving.value, [sessionId]: false }
  }
}

// Oldal betöltésekor egyből lekérjük az adatokat
onMounted(() => {
  minDateTime.value = getCurrentDateTimeLocal()
  fetchMentors()
  fetchSessions()
})
</script>

<template>
  <div class="sessions-page">
    <h2>Foglalkozások (CRUD Teszt)</h2>

    <div v-if="error" class="error-box">{{ error }}</div>

    <div class="create-box">
      <h3>Új időpont foglalása (Create)</h3>
      <form @submit.prevent="createSession" class="inline-form">
        <div>
          <label>Mentor:</label>
          <select v-model="newSession.mentor_profile_id" required class="input">
            <option value="" disabled>Válassz mentort</option>
            <option v-for="mentor in mentors" :key="mentor.id" :value="String(mentor.id)">
              {{ mentor.name }}
            </option>
          </select>
        </div>
        <div>
          <label>Időpont:</label>
          <input type="datetime-local" v-model="newSession.scheduled_time" :min="minDateTime" required class="input" />
        </div>
        <button type="submit" class="btn btn-primary">Létrehozás</button>
      </form>
    </div>

    <div v-if="loading">Betöltés...</div>
    
    <div v-else class="sessions-list">
      <h3>Jelenlegi foglalások (Read)</h3>
      <p v-if="sessions.length === 0">Még nincs egyetlen foglalkozás sem.</p>
      
      <div v-for="session in sessions" :key="session.id" class="session-card">
        <div class="session-info">
          <p>
            <strong>Mentor:</strong>
            {{ mentorByProfileId.get(String(session.mentor_profile_id))?.name || `Profil ID: ${session.mentor_profile_id}` }}
          </p>
          <p><strong>Időpont:</strong> {{ new Date(session.scheduled_time).toLocaleString('hu-HU') }}</p>
          <p>
            <strong>Státusz:</strong> 
            <span :class="['status-badge', session.status]">{{ session.status }}</span>
          </p>
          <p>
            <strong>Előrehaladás:</strong>
            {{ progressBySession[session.id]?.rating ? `${progressBySession[session.id].rating}/5` : 'Nincs értékelés' }}
          </p>
          <p v-if="progressBySession[session.id]?.notes">
            <strong>Megjegyzés:</strong> {{ progressBySession[session.id].notes }}
          </p>

          <div class="progress-editor">
            <h4>Session előrehaladás</h4>
            <label :for="`rating-${session.id}`">Értékelés (1-5)</label>
            <select
              :id="`rating-${session.id}`"
              v-model="progressForms[session.id].rating"
              class="input"
              :disabled="!canRateSession(session)"
            >
              <option value="">Nincs értékelés</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
            </select>
            <small v-if="!canRateSession(session)">Értékelés csak befejezett foglalkozásnál adható.</small>

            <label :for="`notes-${session.id}`">Megjegyzés</label>
            <textarea
              :id="`notes-${session.id}`"
              v-model="progressForms[session.id].notes"
              class="input notes-input"
              rows="3"
              placeholder="Mit gyakoroltatok, miben fejlődött a tanuló?"
            />

            <button
              class="btn btn-primary"
              :disabled="progressSaving[session.id]"
              @click="saveSessionProgress(session)"
            >
              {{ progressSaving[session.id] ? 'Mentés...' : 'Előrehaladás mentése' }}
            </button>
          </div>
        </div>
        
        <div class="session-actions">
          <button @click="updateSessionStatus(session.id, 'completed')" class="btn btn-success" :disabled="session.status === 'completed'">
            Befejezettre állít
          </button>
          <button @click="updateSessionStatus(session.id, 'canceled')" class="btn btn-warning" :disabled="session.status === 'canceled'">
            Lemondás
          </button>
          <button @click="deleteSession(session.id)" class="btn btn-danger">Törlés</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sessions-page { padding: 20px; max-width: 900px; margin: 0 auto; }
h2 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }

.error-box { background: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; margin-bottom: 20px; }

.create-box { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }
.inline-form { display: flex; gap: 15px; align-items: flex-end; }
.input { padding: 8px; border: 1px solid #ccc; border-radius: 4px; }

.session-card { background: #fff; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
.session-info p { margin: 5px 0; }
.progress-editor { margin-top: 12px; padding: 10px; background: #f6f9ff; border: 1px solid #d8e3f4; border-radius: 8px; display: grid; gap: 8px; }
.progress-editor h4 { margin: 0 0 2px; color: #2c3e50; font-size: 0.95rem; }
.notes-input { resize: vertical; min-height: 72px; }

.status-badge { padding: 3px 8px; border-radius: 12px; font-size: 0.85rem; font-weight: bold; }
.status-badge.scheduled { background: #cce5ff; color: #004085; }
.status-badge.completed { background: #d4edda; color: #155724; }
.status-badge.canceled { background: #fff3cd; color: #856404; }

.session-actions { display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end;}
.btn { padding: 8px 12px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; transition: opacity 0.2s; }
.btn:hover { opacity: 0.8; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: #1f67c8; color: white; }
.btn-success { background: #28a745; color: white; }
.btn-warning { background: #ffc107; color: #212529; }
.btn-danger { background: #dc3545; color: white; }
</style>