<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config/api'

const router = useRouter()
const currentUser = ref(null)
const users = ref([])
const languages = ref([])
const pairingSuggestions = ref([])
const mentorResources = ref([])
const loading = ref(false)
const error = ref('')

const getToken = () => localStorage.getItem('token') || localStorage.getItem('access_token')

const isMentor = computed(() => currentUser.value?.role === 'mentor')

const studentPairingSuggestions = computed(() => {
  const studentIds = new Set(users.value.filter((user) => user.role === 'student').map((user) => user.id))
  return pairingSuggestions.value.filter((suggestion) => studentIds.has(suggestion.student_id))
})

const fetchDashboard = async () => {
  loading.value = true
  error.value = ''

  try {
    const token = getToken()
    if (!token) {
      router.push({ name: 'Login' })
      return
    }

    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    }

    const [meResponse, usersResponse, languagesResponse] = await Promise.all([
      fetch(`${API_BASE_URL}/users/me`, { headers }),
      fetch(`${API_BASE_URL}/users`, { headers }),
      fetch(`${API_BASE_URL}/languages`, { headers }),
    ])

    if (meResponse.status === 401 || usersResponse.status === 401 || languagesResponse.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('access_token')
      router.push({ name: 'Login' })
      return
    }

    if (!meResponse.ok || !usersResponse.ok || !languagesResponse.ok) {
      throw new Error('Nem sikerült betölteni a vezérlőpult adatait.')
    }

    const meData = await meResponse.json()
    const usersData = await usersResponse.json()
    const languagesData = await languagesResponse.json()

    currentUser.value = meData
    languages.value = languagesData

    const languageById = new Map(languages.value.map((language) => [language.id, language.name]))

    users.value = usersData.map((user) => {
      const avatarSeed = encodeURIComponent(user.name || `user-${user.id}`)
      return {
        ...user,
        learningLanguageName: user.learning_language_id ? languageById.get(user.learning_language_id) || 'Nincs megadva' : 'Nincs megadva',
        avatarUrl: `https://api.dicebear.com/7.x/initials/svg?seed=${avatarSeed}`,
      }
    })

    if (meData.role === 'mentor') {
      const [pairingsResponse, resourcesResponse] = await Promise.all([
        fetch(`${API_BASE_URL}/pairing-suggestions`, { headers }),
        fetch(`${API_BASE_URL}/mentor-resources`, { headers }),
      ])

      if (pairingsResponse.ok) {
        pairingSuggestions.value = await pairingsResponse.json()
      }
      if (resourcesResponse.ok) {
        mentorResources.value = await resourcesResponse.json()
      }
    } else {
      pairingSuggestions.value = []
      mentorResources.value = []
    }
  } catch (err) {
    error.value = err?.message || 'Hiba történt a vezérlőpult betöltésekor.'
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('access_token')
  router.push({ name: 'Login' })
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <div class="header-spacer"></div>

      <div class="header-center">
        <h2>Vezérlőpult</h2>
        <p v-if="currentUser" class="subhead">
          Bejelentkezve mint <strong>{{ currentUser.name }}</strong>
          <span class="role-pill" :class="currentUser.role">{{ currentUser.role }}</span>
        </p>
      </div>

      <div class="header-actions">
        <button class="refresh-btn" @click="fetchDashboard" :disabled="loading">
          {{ loading ? 'Frissítés...' : 'Frissítés' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
      <button class="retry-btn" @click="fetchDashboard">Újra próbálkozás</button>
    </div>

    <div v-if="loading" class="loading">Betöltés...</div>

    <template v-else>
      <section v-if="isMentor" class="mentor-tools">
        <h3>Mentor / Admin eszközök</h3>
        <div class="tools-grid">
          <article class="tool-card">
            <h4>Párosítási javaslatok</h4>
            <p class="tool-description">A tanulók nyelvi céljai alapján automatikusan illesztett mentor-jelöltek.</p>
            <div v-if="studentPairingSuggestions.length === 0" class="empty-state">Jelenleg nincs javasolt párosítás.</div>
            <div v-else class="suggestion-list">
              <div v-for="suggestion in studentPairingSuggestions" :key="`${suggestion.student_id}-${suggestion.mentor_profile_id}`" class="suggestion-item">
                <strong>{{ suggestion.student_name }}</strong>
                <span>{{ suggestion.learning_language_name || 'Ismeretlen nyelv' }} → {{ suggestion.mentor_name }}</span>
                <small>{{ suggestion.mentor_language_name || 'Nincs megadva' }}</small>
                <small v-if="suggestion.mentor_availability_details">Elérhetőség: {{ suggestion.mentor_availability_details }}</small>
                <small v-if="suggestion.mentor_exchange_terms">Cserefeltétel: {{ suggestion.mentor_exchange_terms }}</small>
                <small v-if="suggestion.match_reason">Illeszkedés: {{ suggestion.match_reason }}</small>
              </div>
            </div>
          </article>

          <article class="tool-card">
            <h4>Erőforrások</h4>
            <p class="tool-description">Hasznos anyagok a hatékony cserealkalmakhoz és a közösségi működéshez.</p>
            <div class="resource-list">
              <a v-for="resource in mentorResources" :key="resource.title" class="resource-item" :href="resource.url" target="_blank" rel="noreferrer">
                <strong>{{ resource.title }}</strong>
                <span>{{ resource.description }}</span>
              </a>
            </div>
          </article>
        </div>
      </section>

      <section class="users-section">
        <h3>Felhasználók</h3>
        <div v-if="users.length > 0" class="users-grid">
          <div v-for="user in users" :key="user.id" class="user-card">
            <div class="card-head">
              <img class="avatar" :src="user.avatarUrl" :alt="`${user.name} profilkep`" />
              <h4>{{ user.name }}</h4>
            </div>
            <p><strong>Email:</strong> {{ user.email }}</p>
            <p><strong>Szerep:</strong> <span class="role" :class="user.role">{{ user.role }}</span></p>
            <p v-if="user.learningLanguageName"><strong>Tanulási cél:</strong> {{ user.learningLanguageName }}</p>
          </div>
        </div>
        <div v-else class="no-users">Nincs megjeleníthető felhasználó.</div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-header {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 14px;
}

.header-center {
  text-align: center;
  white-space: nowrap;
}

.header-center h2 {
  margin: 0;
  color: #2c3e50;
}

.subhead {
  margin: 5px 0 0;
  color: #5b6f83;
  font-size: 0.93rem;
}

.header-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.role-pill {
  display: inline-block;
  margin-left: 8px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 700;
}
.role-pill.mentor { background: #e8f1ff; color: #1f67c8; }
.role-pill.student { background: #dcfce7; color: #166534; }

.refresh-btn,
.retry-btn {
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, opacity 0.2s;
}

.refresh-btn { background-color: #4f46e5; color: white; }
.refresh-btn:hover { background-color: #4338ca; }
.refresh-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.error-message {
  padding: 12px 16px;
  background-color: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 6px;
  color: #fca5a5;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.retry-btn { padding: 6px 12px; background-color: #ef4444; color: white; font-size: 0.9rem; }
.retry-btn:hover { background-color: #dc2626; }

.loading { text-align: center; padding: 40px 20px; color: #cbd5e1; font-size: 1.1rem; }

.mentor-tools { margin-bottom: 28px; }
.mentor-tools h3,
.users-section h3 { margin: 0 0 14px; color: #f1f5f9; }

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.tool-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.tool-card h4 { margin: 0 0 8px; color: #f1f5f9; }
.tool-description { margin: 0 0 12px; color: #cbd5e1; font-size: 0.95rem; }

.suggestion-list,
.resource-list { display: grid; gap: 10px; }

.suggestion-item,
.resource-item {
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 10px;
  padding: 12px;
  background: rgba(99, 102, 241, 0.08);
  display: grid;
  gap: 4px;
}

.resource-item { text-decoration: none; color: #f1f5f9; }
.resource-item span,
.suggestion-item span { color: #cbd5e1; font-size: 0.92rem; }

.empty-state { color: #cbd5e1; font-size: 0.95rem; padding: 6px 0; }

.users-section { margin-top: 12px; }

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.user-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.user-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.15);
}

.card-head { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }

.avatar {
  width: 46px;
  height: 46px;
  border-radius: 999px;
  border: 2px solid rgba(99, 102, 241, 0.3);
  background: rgba(99, 102, 241, 0.1);
}

.user-card h4 { margin: 0; color: #f1f5f9; }
.user-card p { margin: 8px 0; color: #cbd5e1; font-size: 0.95rem; }

.role {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: bold;
}
.role.mentor { background-color: rgba(99, 102, 241, 0.25); color: #818cf8; }
.role.student { background-color: rgba(34, 197, 94, 0.25); color: #86efac; }

.no-users { text-align: center; padding: 40px 20px; color: #cbd5e1; font-size: 1rem; }

@media (max-width: 760px) {
  .dashboard-header {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .header-spacer { display: none; }
  .header-actions { justify-content: center; }
  .error-message { flex-direction: column; align-items: flex-start; }
}
</style>