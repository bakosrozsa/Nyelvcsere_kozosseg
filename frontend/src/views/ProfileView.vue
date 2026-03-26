<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const user = ref(null)
const loading = ref(false)
const error = ref('')

const API_BASE_URL = 'http://127.0.0.1:8000'

const fetchCurrentUser = async () => {
  loading.value = true
  error.value = ''

  try {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('Nincs token. Kérjük, jelentkezzen be.')
    }

    const response = await fetch(`${API_BASE_URL}/users/1`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error('Nem sikerült lekérni a profilt.')
    }

    const data = await response.json()
    user.value = data
  } catch (err) {
    error.value = err.message || 'Hiba történt.'
  } finally {
    loading.value = false
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
</style>
