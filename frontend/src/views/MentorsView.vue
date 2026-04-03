<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const mentors = ref([])
const currentUser = ref(null)
const loading = ref(false)
const error = ref('')
const actionMessage = ref('')
const isAuthenticated = ref(false)

const searchText = ref('')
const languageFilter = ref('all')
const selectedMentorId = ref(null)
const bookingDateTime = ref('')
const bookingLoading = ref(false)
const minBookingDateTime = ref('')

const API_BASE_URL = 'http://127.0.0.1:8000'

const getStoredToken = () => localStorage.getItem('token') || localStorage.getItem('access_token')

const syncAuthState = () => {
  isAuthenticated.value = !!getStoredToken()
}

const formatDefaultBookingTime = () => {
  const now = new Date()
  now.setHours(now.getHours() + 1)
  now.setMinutes(0, 0, 0)
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const formatMinBookingTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const availableLanguages = computed(() => {
  const values = mentors.value.map((m) => m.teachesLanguage).filter(Boolean)
  return [...new Set(values)].sort((a, b) => a.localeCompare(b))
})

const filteredMentors = computed(() => {
  const query = searchText.value.trim().toLowerCase()
  return mentors.value.filter((mentor) => {
    if (currentUser.value?.role === 'mentor' && mentor.userId === currentUser.value.id) {
      return false
    }
    const matchesText =
      query.length === 0 ||
      mentor.mentorName.toLowerCase().includes(query) ||
      mentor.mentorEmail.toLowerCase().includes(query)
    const matchesLanguage =
      languageFilter.value === 'all' || mentor.teachesLanguage === languageFilter.value
    return matchesText && matchesLanguage
  })
})

const canBookMentor = computed(() => isAuthenticated.value && currentUser.value?.role !== 'mentor')

const fetchMentors = async () => {
  loading.value = true
  error.value = ''

  try {
    const token = getStoredToken()
    
    const headers = {
      'Content-Type': 'application/json',
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const [profilesRes, usersRes, languagesRes] = await Promise.all([
      fetch(`${API_BASE_URL}/mentor-profiles`, { headers }),
      fetch(`${API_BASE_URL}/users`, { headers }),
      fetch(`${API_BASE_URL}/languages`, { headers }),
    ])

    if (token && (profilesRes.status === 401 || usersRes.status === 401 || languagesRes.status === 401)) {
      localStorage.removeItem('token')
      router.push({ name: 'Login' })
      return
    }

    if (!profilesRes.ok || !usersRes.ok || !languagesRes.ok) {
      throw new Error('Nem sikerült betölteni a mentor adatokat.')
    }

    const [profiles, users, languages] = await Promise.all([
      profilesRes.json(),
      usersRes.json(),
      languagesRes.json(),
    ])

    const usersById = new Map(users.map((u) => [u.id, u]))
    const languagesById = new Map(languages.map((l) => [l.id, l]))

    mentors.value = profiles
      .map((profile) => {
        const user = usersById.get(profile.user_id)
        if (!user) return null

        const avatarSeed = encodeURIComponent(user.name || `mentor-${profile.id}`)
        const avatarUrl = `https://api.dicebear.com/7.x/initials/svg?seed=${avatarSeed}`

        return {
          id: profile.id,
          userId: user.id,
          mentorName: user.name,
          mentorEmail: user.email,
          teachesLanguage: languagesById.get(profile.offered_language_id)?.name || 'Nincs megadva',
          learnsLanguage: languagesById.get(profile.requested_language_id)?.name || 'Nincs megadva',
          sessionLength: profile.session_length_minutes || 60,
          availabilityDetails: profile.availability_details || 'Nincs megadva',
          exchangeTerms: profile.exchange_terms || 'Nincs megadva',
          avatarUrl,
        }
      })
      .filter(Boolean)
  } catch (err) {
    error.value = err?.message || 'Hiba történt a mentorok betöltésekor.'
  } finally {
    loading.value = false
  }
}

const fetchCurrentUser = async () => {
  try {
    const token = getStoredToken()
    if (!token) {
      currentUser.value = null
      return
    }

    const response = await fetch(`${API_BASE_URL}/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      currentUser.value = null
      return
    }

    currentUser.value = await response.json()
  } catch (err) {
    currentUser.value = null
    console.error(err)
  }
}

const toggleBooking = (mentorId) => {
  if (currentUser.value?.role === 'mentor') {
    actionMessage.value = 'Mentorkent nem foglalhatsz idopontot, csak a hozzad foglaltakat kezelheted.'
    return
  }

  if (!isAuthenticated.value) {
    actionMessage.value = 'A foglalashoz jelentkezz be.'
    return
  }
  actionMessage.value = ''
  minBookingDateTime.value = formatMinBookingTime()
  if (selectedMentorId.value === mentorId) {
    selectedMentorId.value = null
    return
  }
  selectedMentorId.value = mentorId
  bookingDateTime.value = formatDefaultBookingTime()
}

const handleBooking = async (mentor) => {
  actionMessage.value = ''
  syncAuthState()

  if (currentUser.value?.role === 'mentor') {
    actionMessage.value = 'Mentorkent nem foglalhatsz idopontot, csak a hozzad foglaltakat kezelheted.'
    return
  }

  const token = getStoredToken()
  if (!token) {
    router.push({ name: 'Login', query: { redirect: '/mentors' } })
    return
  }

  if (!bookingDateTime.value) {
    actionMessage.value = 'Valassz idopontot a foglalashoz.'
    return
  }

  const selectedDate = new Date(bookingDateTime.value)
  if (Number.isNaN(selectedDate.getTime()) || selectedDate.getTime() < Date.now()) {
    actionMessage.value = 'Csak a jelenlegi idoponttol kezdve lehet foglalni.'
    return
  }

  bookingLoading.value = true
  try {
    const response = await fetch(`${API_BASE_URL}/sessions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mentor_profile_id: mentor.id,
        scheduled_time: new Date(bookingDateTime.value).toISOString(),
      }),
    })

    if (response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('access_token')
      router.push({ name: 'Login' })
      return
    }

    if (!response.ok) {
      let errorDetail = 'A foglalas nem sikerult. Probald ujra.'
      try {
        const data = await response.json()
        if (data?.detail) {
          errorDetail = data.detail
        }
      } catch {
        // Keep default error message when response body is not JSON.
      }
      throw new Error(errorDetail)
    }

    actionMessage.value = `${mentor.mentorName} mentorhoz a foglalas sikeres.`
    selectedMentorId.value = null
  } catch (err) {
    actionMessage.value = err?.message || 'Hiba tortent foglalas kozben.'
  } finally {
    bookingLoading.value = false
  }
}

onMounted(() => {
  syncAuthState()
  Promise.all([fetchCurrentUser(), fetchMentors()]).then(() => {
    syncAuthState()
  })
})
</script>

<template>
  <section class="mentors-page">
    <header class="page-header">
      <h2>Mentorok</h2>
      <button class="refresh-btn" @click="fetchMentors" :disabled="loading">
        {{ loading ? 'Frissítés...' : 'Frissítés' }}
      </button>
    </header>

    <div class="filters">
      <input
        v-model="searchText"
        type="text"
        class="filter-input"
        placeholder="Kereses nev vagy email alapjan"
      />
      <select v-model="languageFilter" class="filter-select">
        <option value="all">Minden tanitott nyelv</option>
        <option v-for="language in availableLanguages" :key="language" :value="language">
          {{ language }}
        </option>
      </select>
    </div>

    <p v-if="actionMessage" class="action-message">{{ actionMessage }}</p>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="loading" class="info">Mentorok betöltése...</p>
    <p v-else-if="filteredMentors.length === 0" class="info">Nincs talalat a szureshez.</p>

    <div v-else class="grid">
      <article v-for="mentor in filteredMentors" :key="mentor.id" class="card">
        <div class="card-head">
          <img class="avatar" :src="mentor.avatarUrl" :alt="`${mentor.mentorName} profilkep`" />
          <div>
            <h3>{{ mentor.mentorName }}</h3>
            <p class="email">{{ mentor.mentorEmail }}</p>
          </div>
        </div>

        <div class="meta">
          <p><strong>Tanított nyelv:</strong> {{ mentor.teachesLanguage }}</p>
          <p><strong>Tanulni szeretné:</strong> {{ mentor.learnsLanguage }}</p>
          <p><strong>Foglalkozás hossza:</strong> {{ mentor.sessionLength }} perc</p>
          <p><strong>Elérhetőség:</strong> {{ mentor.availabilityDetails }}</p>
          <p><strong>Csere feltételei:</strong> {{ mentor.exchangeTerms }}</p>
        </div>

        <div class="card-actions">
          <button v-if="canBookMentor" class="book-btn" @click="toggleBooking(mentor.id)">
            {{ selectedMentorId === mentor.id ? 'Mégse' : 'Foglalás' }}
          </button>
          <p v-else-if="isAuthenticated && currentUser?.role === 'mentor'" class="mentor-booking-disabled">
            Mentorkent itt nem foglalhatsz idopontot.
          </p>
          <router-link v-else class="guest-book-link" :to="{ name: 'Login', query: { redirect: '/mentors' } }">
            Bejelentkezes a foglalashoz
          </router-link>
        </div>

        <div v-if="canBookMentor && selectedMentorId === mentor.id" class="booking-panel">
          <label class="booking-label" :for="`booking-${mentor.id}`">Valassz idopontot</label>
          <input
            :id="`booking-${mentor.id}`"
            v-model="bookingDateTime"
            type="datetime-local"
            class="booking-input"
            :min="minBookingDateTime"
          />
          <button class="confirm-booking" :disabled="bookingLoading" @click="handleBooking(mentor)">
            {{ bookingLoading ? 'Foglalas...' : 'Foglalas megerositese' }}
          </button>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.mentors-page {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.page-header h2 {
  margin: 0;
  color: #f1f5f9;
}

.refresh-btn {
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  background: #4f46e5;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.refresh-btn:disabled {
  opacity: 0.7;
  cursor: wait;
}

.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  padding: 10px 12px;
  border-radius: 8px;
}

.info {
  color: #cbd5e1;
}

.action-message {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #86efac;
  padding: 10px 12px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.filters {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
  gap: 10px;
  margin-bottom: 14px;
  width: 100%;
}

.filter-input,
.filter-select,
.booking-input {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.06);
  color: #f1f5f9;
  font-size: 0.95rem;
  outline: none;
}

.filter-input::placeholder,
.booking-input::placeholder {
  color: #cbd5e1;
}

.filter-input:focus,
.filter-select:focus,
.booking-input:focus {
  border-color: #4f46e5;
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.12);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
  border-color: rgba(99, 102, 241, 0.3);
}

.card-head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.avatar {
  width: 46px;
  height: 46px;
  border-radius: 999px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  background: rgba(99, 102, 241, 0.1);
}

.card h3 {
  margin: 0 0 6px;
  color: #f1f5f9;
}

.email {
  margin: 0 0 12px;
  color: #cbd5e1;
  font-size: 0.95rem;
}

.meta p {
  margin: 6px 0;
  color: #cbd5e1;
}

.card-actions {
  margin-top: 12px;
}

.mentor-booking-disabled {
  margin: 0;
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.12);
  border: 1px solid rgba(251, 191, 36, 0.2);
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 0.9rem;
}

.book-btn,
.confirm-booking {
  border: none;
  border-radius: 8px;
  padding: 9px 12px;
  font-weight: 600;
  cursor: pointer;
}

.book-btn {
  background: #4f46e5;
  color: #ffffff;
}

.guest-book-link {
  display: inline-block;
  text-decoration: none;
  border-radius: 8px;
  padding: 9px 12px;
  font-weight: 600;
  color: #818cf8;
  border: 1px solid rgba(99, 102, 241, 0.3);
  background: rgba(99, 102, 241, 0.08);
}

.confirm-booking {
  background: #22c55e;
  color: #ffffff;
}

.confirm-booking:disabled {
  opacity: 0.7;
  cursor: wait;
}

.booking-panel {
  margin-top: 12px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 10px;
  padding: 10px;
  display: grid;
  gap: 8px;
}

.booking-label {
  font-size: 0.88rem;
  font-weight: 600;
  color: #f1f5f9;
}

@media (max-width: 760px) {
  .filters {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .filter-input,
  .filter-select {
    font-size: 0.92rem;
  }
}
</style>