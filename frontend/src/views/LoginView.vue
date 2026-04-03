<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const router = useRouter()

const handleLogin = async () => {
  errorMessage.value = ''
  loading.value = true

  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const response = await axios.post('http://127.0.0.1:8000/login', formData)

    const token = response.data.access_token
    localStorage.setItem('token', token)

    router.push('/dashboard')
  } catch (error) {
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'Hibás email vagy jelszó!'
    } else {
      errorMessage.value = 'Szerver hiba. Kérlek próbáld újra később.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <div class="login-card">
      <div class="card-icon">💬</div>
      <h1 class="title">Bejelentkezés</h1>
      <p class="subtitle">Lépj be a Nyelvcsere közösségbe.</p>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="field-group">
          <label class="label" for="email">Email</label>
          <input
            id="email"
            v-model="email"
            class="input"
            type="email"
            placeholder="pelda@email.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="field-group">
          <label class="label" for="password">Jelszó</label>
          <input
            id="password"
            v-model="password"
            class="input"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

        <button class="submit" type="submit" :disabled="loading">
          {{ loading ? 'Belépés...' : 'Belépés' }}
        </button>
      </form>

      <p class="switch-link">
        Nincs még fiókod?
        <a href="#" @click.prevent="$router.push('/register')">Regisztrálj itt!</a>
      </p>
    </div>
  </main>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.12) 0%, transparent 55%),
    radial-gradient(ellipse at 60% 85%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    linear-gradient(135deg, #0f1623 0%, #161d2e 50%, #0f1420 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 36px 32px;
  box-shadow:
    0 25px 60px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(20px);
  text-align: center;
}

.card-icon {
  font-size: 2rem;
  margin-bottom: 12px;
  display: block;
}

.title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 8px 0 28px;
  color: #94a3b8;
  font-size: 0.93rem;
}

.login-form {
  display: grid;
  gap: 16px;
  text-align: left;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 0.82rem;
  font-weight: 600;
  color: #cbd5e1;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.input {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 11px 14px;
  font-size: 0.95rem;
  color: #f1f5f9;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.input::placeholder {
  color: #475569;
}

.input:focus {
  border-color: rgba(99, 102, 241, 0.7);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  background: rgba(255, 255, 255, 0.09);
}

.error {
  margin: 0;
  color: #f87171;
  font-size: 0.88rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 8px;
  padding: 8px 12px;
}

.submit {
  margin-top: 4px;
  border: none;
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 0.95rem;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #4f46e5, #6366f1);
  cursor: pointer;
  transition: opacity 0.2s, transform 0.15s, box-shadow 0.2s;
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
  letter-spacing: 0.02em;
}

.submit:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-1px);
  box-shadow: 0 6px 22px rgba(99, 102, 241, 0.45);
}

.submit:active:not(:disabled) {
  transform: translateY(0);
}

.submit:disabled {
  opacity: 0.55;
  cursor: wait;
}

.switch-link {
  margin-top: 20px;
  color: #64748b;
  font-size: 0.88rem;
  text-align: center;
}

.switch-link a {
  color: #818cf8;
  font-weight: 600;
  text-decoration: none;
}

.switch-link a:hover {
  color: #a5b4fc;
  text-decoration: underline;
}
</style>