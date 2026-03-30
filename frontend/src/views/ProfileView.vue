<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const mentorProfile = ref(null)
const languages = ref([])
const offeredLanguageId = ref('')
const requestedLanguageId = ref('')
const saveLoading = ref(false)
const saveMessage = ref('')
const loading = ref(false)
const error = ref('')

const API_BASE_URL = 'http://127.0.0.1:8000'

const getToken = () => localStorage.getItem('token') || localStorage.getItem('access_token')

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

onMounted(() => {
  fetchCurrentUser()
})
</script>

<template>
  <div class="profile">
    <h2>Profil</h2>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading" class="loading">Betöltés...</div>

    <div v-if="user" class="profile-info">
      <p><strong>Név:</strong> {{ user.name }}</p>
      <p><strong>Email:</strong> {{ user.email }}</p>
      <p><strong>Szerep:</strong> {{ user.role }}</p>

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
          <option v-for="language in languages" :key="`request-${language.id}`" :value="String(language.id)">
            {{ language.name }}
          </option>
        </select>

        <button type="submit" :disabled="saveLoading">
          {{ saveLoading ? 'Mentes...' : 'Mentor nyelvek mentese' }}
        </button>

        <p v-if="saveMessage" class="save-message">{{ saveMessage }}</p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.profile {
  padding: 20px;
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
.mentor-form button {
  border: 1px solid #cfd9e3;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 0.95rem;
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
</style>
