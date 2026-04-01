<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentUser = ref(null)
const users = ref([])
const languages = ref([])
const pairingSuggestions = ref([])
const mentorResources = ref([])
const loading = ref(false)
const error = ref('')

const API_BASE_URL = 'http://127.0.0.1:8000'

const getToken = () => localStorage.getItem('token') || localStorage.getItem('access_token')

const isMentor = computed(() => currentUser.value?.role === 'mentor')

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
      <div>
        <h2>Vezérlőpult</h2>
        <p v-if="currentUser" class="subhead">
          Bejelentkezve mint <strong>{{ currentUser.name }}</strong>
          <span class="role-pill">{{ currentUser.role }}</span>
        </p>
      </div>
      <div class="header-actions">
        <button class="refresh-btn" @click="fetchDashboard" :disabled="loading">
          {{ loading ? 'Frissítés...' : 'Frissítés' }}
        </button>
        <button class="logout-btn" @click="handleLogout">Kijelentkezés</button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
      <button class="retry-btn" @click="fetchDashboard">Újra próbálkozás</button>
    </div>

    <div v-if="loading" class="loading">
      Betöltés...
    </div>

    <template v-else>
      <section v-if="isMentor" class="mentor-tools">
        <h3>Mentor / Admin eszközök</h3>

        <div class="tools-grid">
          <article class="tool-card">
            <h4>Párosítási javaslatok</h4>
            <p class="tool-description">
              A tanulók nyelvi céljai alapján automatikusan illesztett mentor-jelöltek.
            </p>
            <div v-if="pairingSuggestions.length === 0" class="empty-state">
              Jelenleg nincs javasolt párosítás.
            </div>
            <div v-else class="suggestion-list">
              <div v-for="suggestion in pairingSuggestions" :key="`${suggestion.student_id}-${suggestion.mentor_profile_id}`" class="suggestion-item">
                <strong>{{ suggestion.student_name }}</strong>
                <span>
                  {{ suggestion.learning_language_name || 'Ismeretlen nyelv' }} → {{ suggestion.mentor_name }}
                </span>
                <small>{{ suggestion.mentor_language_name || 'Nincs megadva' }}</small>
                <small v-if="suggestion.mentor_availability_details">
                  Elérhetőség: {{ suggestion.mentor_availability_details }}
                </small>
                <small v-if="suggestion.mentor_exchange_terms">
                  Cserefeltétel: {{ suggestion.mentor_exchange_terms }}
                </small>
                <small v-if="suggestion.match_reason">
                  Illeszkedés: {{ suggestion.match_reason }}
                </small>
              </div>
            </div>
          </article>

          <article class="tool-card">
            <h4>Erőforrások</h4>
            <p class="tool-description">
              Hasznos anyagok a hatékony cserealkalmakhoz és a közösségi működéshez.
            </p>
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
        <div v-else class="no-users">
          Nincs megjeleníthető felhasználó.
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 20px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 10px;
}

.dashboard-header h2 {
  margin: 0;
  color: #2c3e50;
}

.subhead {
  margin: 6px 0 0;
  color: #5b6f83;
}

.role-pill {
  display: inline-block;
  margin-left: 8px;
  padding: 3px 8px;
  border-radius: 999px;
  background: #e8f1ff;
  color: #1f67c8;
  font-size: 0.85rem;
  font-weight: 700;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.refresh-btn,
.logout-btn,
.retry-btn {
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s, opacity 0.2s;
}

.refresh-btn {
  background-color: #1f67c8;
  color: white;
}

.logout-btn {
  background-color: #dc3545;
  color: white;
}

.refresh-btn:hover {
  background-color: #1653a2;
}

.logout-btn:hover {
  background-color: #c82333;
}

.error-message {
  padding: 12px 16px;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 6px;
  color: #721c24;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.retry-btn {
  padding: 6px 12px;
  background-color: #721c24;
  color: white;
  font-size: 0.9rem;
}

.retry-btn:hover {
  background-color: #5a131a;
}

.loading {
  text-align: center;
  padding: 40px 20px;
  color: #666;
  font-size: 1.1rem;
}

.mentor-tools {
  margin-bottom: 28px;
}

.mentor-tools h3,
.users-section h3 {
  margin: 0 0 14px;
  color: #2c3e50;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.tool-card {
  background: white;
  border: 1px solid #d9e2ec;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 18px rgba(14, 29, 52, 0.08);
}

.tool-card h4 {
  margin: 0 0 8px;
  color: #1d3247;
}

.tool-description {
  margin: 0 0 12px;
  color: #5b6f83;
  font-size: 0.95rem;
}

.suggestion-list,
.resource-list,
.interaction-list {
  display: grid;
  gap: 10px;
}

.suggestion-item,
.resource-item {
  border: 1px solid #dde6f1;
  border-radius: 10px;
  padding: 12px;
  background: #f8fbff;
  display: grid;
  gap: 4px;
}

.resource-item {
  text-decoration: none;
  color: inherit;
}

.resource-item span,
.suggestion-item span,
.interaction-list span {
  color: #5b6f83;
  font-size: 0.92rem;
}

.interaction-block {
  margin-top: 12px;
}

.matched-students {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #d7e2ef;
}

.matched-students h5 {
  margin: 0 0 6px;
  color: #22354b;
  font-size: 0.92rem;
}

.matched-students ul {
  margin: 0;
  padding-left: 18px;
  color: #4f6378;
  display: grid;
  gap: 4px;
}

.interaction-block h5 {
  margin: 0 0 8px;
  color: #22354b;
}

.empty-state {
  color: #7b8794;
  font-size: 0.95rem;
  padding: 6px 0;
}

.users-section {
  margin-top: 12px;
}

.users-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.user-card {
  background: white;
  border: 1px solid #d9e2ec;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 6px 18px rgba(14, 29, 52, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.user-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 28px rgba(14, 29, 52, 0.16);
  border-color: #bfd3eb;
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
  border: 2px solid #d9e6f5;
  background: #f5f9ff;
}

.user-card h4 {
  margin: 0;
  color: #2c3e50;
}

.user-card p {
  margin: 8px 0;
  color: #555;
  font-size: 0.95rem;
}

.role {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: bold;
}

.role.mentor {
  background-color: #d1ecf1;
  color: #0c5460;
}

.role.student {
  background-color: #d4edda;
  color: #155724;
}

.no-users {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 1rem;
}

@media (max-width: 760px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .error-message {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
