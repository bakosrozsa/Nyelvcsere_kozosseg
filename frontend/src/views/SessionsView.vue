<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'
const sessions = ref([])
const loading = ref(false)
const error = ref('')

// Űrlap adatai az új foglaláshoz (Create)
const newSession = ref({
  mentor_profile_id: 1, // Alapértelmezett ID, ezt később lehetne dinamikussá tenni
  scheduled_time: ''
})

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
  } catch (err) {
    error.value = 'Hiba a foglalkozások lekérésekor.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// --- 2. CREATE (Létrehozás) ---
const createSession = async () => {
  if (!newSession.value.scheduled_time) return
  
  try {
    // Formázzuk a dátumot a backendnek megfelelő ISO formátumra
    const payload = {
      mentor_profile_id: newSession.value.mentor_profile_id,
      scheduled_time: new Date(newSession.value.scheduled_time).toISOString()
    }
    await axios.post(`${API_BASE_URL}/sessions`, payload, { headers: getHeaders() })
    
    // Sikeres mentés után frissítjük a listát és kiürítjük az űrlapot
    fetchSessions()
    newSession.value.scheduled_time = ''
    alert('Sikeres időpontfoglalás!')
  } catch (err) {
    alert('Hiba történt a létrehozás során.')
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

// Oldal betöltésekor egyből lekérjük az adatokat
onMounted(() => {
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
          <label>Mentor ID:</label>
          <input type="number" v-model="newSession.mentor_profile_id" min="1" required class="input" />
        </div>
        <div>
          <label>Időpont:</label>
          <input type="datetime-local" v-model="newSession.scheduled_time" required class="input" />
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
          <p><strong>ID:</strong> {{ session.id }}</p>
          <p><strong>Mentor Profile ID:</strong> {{ session.mentor_profile_id }}</p>
          <p><strong>Időpont:</strong> {{ new Date(session.scheduled_time).toLocaleString('hu-HU') }}</p>
          <p>
            <strong>Státusz:</strong> 
            <span :class="['status-badge', session.status]">{{ session.status }}</span>
          </p>
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