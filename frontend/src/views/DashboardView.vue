<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const users = ref([])
const loading = ref(false)
const error = ref('')

const API_BASE_URL = 'http://127.0.0.1:8000'

const fetchUsers = async () => {
  loading.value = true
  error.value = ''

  try {
    // JAVÍTVA: 'access_token' helyett 'token'
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('No token found. Please log in.')
    }

    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      if (response.status === 401) {
        // JAVÍTVA: 'access_token' helyett 'token'
        localStorage.removeItem('token')
        router.push({ name: 'Login' })
        throw new Error('Session expired. Please log in again.')
      }
      throw new Error(`Failed to fetch users: ${response.statusText}`)
    }

    const data = await response.json()
    users.value = data.map((user) => {
      const avatarSeed = encodeURIComponent(user.name || `user-${user.id}`)
      return {
        ...user,
        avatarUrl: `https://api.dicebear.com/7.x/initials/svg?seed=${avatarSeed}`,
      }
    })
  } catch (err) {
    error.value = err.message || 'An error occurred while fetching users.'
    console.error(error.value)
  } finally {
    loading.value = false
  }
}

const handleLogout = () => {
  // JAVÍTVA: 'access_token' helyett 'token'
  localStorage.removeItem('token')
  router.push({ name: 'Login' })
}

onMounted(() => {
  fetchUsers()
})
</script>

<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h2>Felhasználók</h2>
      <button class="logout-btn" @click="handleLogout">Kijelentkezés</button>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
      <button class="retry-btn" @click="fetchUsers">Újra próbálkozás</button>
    </div>

    <div v-if="loading" class="loading">
      Betöltés...
    </div>

    <div v-else-if="users.length > 0" class="users-grid">
      <div v-for="user in users" :key="user.id" class="user-card">
        <div class="card-head">
          <img class="avatar" :src="user.avatarUrl" :alt="`${user.name} profilkep`" />
          <h3>{{ user.name }}</h3>
        </div>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><strong>Szerep:</strong> <span class="role" :class="user.role">{{ user.role }}</span></p>
        <p><strong>ID:</strong> {{ user.id }}</p>
      </div>
    </div>

    <div v-else class="no-users">
      Nincs megjeleníthető felhasználó.
    </div>
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
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 10px;
}

.dashboard-header h2 {
  margin: 0;
  color: #2c3e50;
}

.logout-btn {
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  background-color: #dc3545;
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
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
}

.retry-btn {
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  background-color: #721c24;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
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

.user-card h3 {
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
</style>