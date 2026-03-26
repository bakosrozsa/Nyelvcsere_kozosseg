<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const mentors = ref([])
const loading = ref(false)
const error = ref('')

const API_BASE_URL = 'http://127.0.0.1:8000'

const fetchMentors = async () => {
  loading.value = true
  error.value = ''

  try {
    // JAVÍTVA: access_token -> token
    const token = localStorage.getItem('token')
    if (!token) {
      router.push({ name: 'Login' })
      return
    }

    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    }

    const [profilesRes, usersRes, languagesRes] = await Promise.all([
      fetch(`${API_BASE_URL}/mentor-profiles`, { headers }),
      fetch(`${API_BASE_URL}/users`, { headers }),
      fetch(`${API_BASE_URL}/languages`, { headers }),
    ])

    if (profilesRes.status === 401 || usersRes.status === 401 || languagesRes.status === 401) {
      // JAVÍTVA: access_token -> token
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

        return {
          id: profile.id,
          mentorName: user.name,
          mentorEmail: user.email,
          teachesLanguage: languagesById.get(profile.offered_language_id)?.name || 'Nincs megadva',
          learnsLanguage: languagesById.get(profile.requested_language_id)?.name || 'Nincs megadva',
          sessionLength: profile.session_length_minutes || 60,
        }
      })
      .filter(Boolean)
  } catch (err) {
    error.value = err?.message || 'Hiba történt a mentorok betöltésekor.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchMentors)
</script>

<template>
  <section class="mentors-page">
    <header class="page-header">
      <h2>Mentorok</h2>
      <button class="refresh-btn" @click="fetchMentors" :disabled="loading">
        {{ loading ? 'Frissítés...' : 'Frissítés' }}
      </button>
    </header>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-else-if="loading" class="info">Mentorok betöltése...</p>
    <p v-else-if="mentors.length === 0" class="info">Jelenleg nincs elérhető mentor.</p>

    <div v-else class="grid">
      <article v-for="mentor in mentors" :key="mentor.id" class="card">
        <h3>{{ mentor.mentorName }}</h3>
        <p class="email">{{ mentor.mentorEmail }}</p>

        <div class="meta">
          <p><strong>Tanított nyelv:</strong> {{ mentor.teachesLanguage }}</p>
          <p><strong>Tanulni szeretné:</strong> {{ mentor.learnsLanguage }}</p>
          <p><strong>Foglalkozás hossza:</strong> {{ mentor.sessionLength }} perc</p>
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
  color: #22354b;
}

.refresh-btn {
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  background: #1f67c8;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.refresh-btn:disabled {
  opacity: 0.7;
  cursor: wait;
}

.error {
  background: #ffe2e2;
  border: 1px solid #ffc9c9;
  color: #8f1d1d;
  padding: 10px 12px;
  border-radius: 8px;
}

.info {
  color: #5a6775;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.card {
  background: #fff;
  border: 1px solid #d9e2ec;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 18px rgba(14, 29, 52, 0.08);
}

.card h3 {
  margin: 0 0 6px;
  color: #1d3247;
}

.email {
  margin: 0 0 12px;
  color: #5b6f83;
  font-size: 0.95rem;
}

.meta p {
  margin: 6px 0;
  color: #2d3f52;
}
</style>