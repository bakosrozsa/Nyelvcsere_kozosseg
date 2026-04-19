<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { API_BASE_URL } from '../config/api'

const router = useRouter()
const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('student')
const learningLanguageId = ref('')
const offeredLanguageId = ref('')
const requestedLanguageId = ref('')
const availabilityDetails = ref('')
const exchangeTerms = ref('')
const languages = ref([])
const loading = ref(false)
const error = ref('')

const fetchLanguages = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/languages`)
    if (!response.ok) throw new Error('Nem sikerult a nyelveket betolteni.')
    languages.value = await response.json()
  } catch (err) {
    error.value = err?.message || 'Hiba tortent a nyelvek lekerese soran.'
  }
}

const getAvailableRequestedLanguages = () => {
  if (!offeredLanguageId.value) return languages.value
  return languages.value.filter((lang) => String(lang.id) !== String(offeredLanguageId.value))
}

const handleRegister = async () => {
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = 'A jelszavak nem egyeznek.'
    return
  }

  if (role.value === 'student' && !learningLanguageId.value) {
    error.value = 'Kérlek, válassz egy tanulni kívánt nyelvet.'
    return
  }

  if (role.value === 'mentor' && offeredLanguageId.value && requestedLanguageId.value) {
    if (Number(offeredLanguageId.value) === Number(requestedLanguageId.value)) {
      error.value = 'A tanított és tanult nyelvek nem lehetnek azonosak!'
      return
    }
  }

  loading.value = true

  try {
    const payload = {
      name: name.value,
      email: email.value,
      password: password.value,
      role: role.value,
    }

    if (role.value === 'student') {
      payload.learning_language_id = Number(learningLanguageId.value)
    }

    if (role.value === 'mentor') {
      payload.offered_language_id = offeredLanguageId.value ? Number(offeredLanguageId.value) : null
      payload.requested_language_id = requestedLanguageId.value ? Number(requestedLanguageId.value) : null
      payload.availability_details = availabilityDetails.value?.trim() || null
      payload.exchange_terms = exchangeTerms.value?.trim() || null
    }

    const response = await fetch(`${API_BASE_URL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Regisztráció sikertelen.')
    }

    router.push({ name: 'Login', query: { message: 'Sikeres regisztráció! Kérjük, jelentkezzen be.' } })
  } catch (err) {
    error.value = err.message || 'Hiba történt a regisztráció során.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchLanguages)
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <div class="card-icon">🌐</div>
      <h1>Regisztráció</h1>
      <p class="subtitle">Csatlakozz a Nyelvcsere közösséghez.</p>

      <form class="register-form" @submit.prevent="handleRegister">
        <div class="field-group">
          <label class="label" for="name">Név</label>
          <input id="name" v-model="name" class="input" type="text" placeholder="Teljes név" required />
        </div>

        <div class="field-group">
          <label class="label" for="email">Email</label>
          <input id="email" v-model="email" class="input" type="email" placeholder="pelda@email.com" required />
        </div>

        <div class="field-group">
          <label class="label" for="role">Szerep</label>
          <select id="role" v-model="role" class="input">
            <option value="student">Diák</option>
            <option value="mentor">Mentor</option>
          </select>
        </div>

        <template v-if="role === 'student'">
          <div class="field-group">
            <label class="label" for="learningLanguage">Tanulni kívánt nyelv</label>
            <select id="learningLanguage" v-model="learningLanguageId" class="input" required>
              <option value="">Válassz nyelvet</option>
              <option v-for="language in languages" :key="`learning-${language.id}`" :value="language.id">
                {{ language.name }}
              </option>
            </select>
          </div>
        </template>

        <template v-if="role === 'mentor'">
          <div class="field-group">
            <label class="label" for="offeredLanguage">Tanított nyelv</label>
            <select id="offeredLanguage" v-model="offeredLanguageId" class="input">
              <option value="">Válassz nyelvet</option>
              <option v-for="language in languages" :key="language.id" :value="language.id">
                {{ language.name }}
              </option>
            </select>
          </div>

          <div class="field-group">
            <label class="label" for="requestedLanguage">Tanulni vágyott nyelv</label>
            <select id="requestedLanguage" v-model="requestedLanguageId" class="input">
              <option value="">Válassz nyelvet</option>
              <option v-for="language in getAvailableRequestedLanguages()" :key="`requested-${language.id}`" :value="language.id">
                {{ language.name }}
              </option>
            </select>
          </div>

          <div class="field-group">
            <label class="label" for="availabilityDetails">Elérhetőség</label>
            <textarea
              id="availabilityDetails"
              v-model="availabilityDetails"
              class="input textarea"
              rows="3"
              placeholder="Pl.: Hétköznap esténként 18:00 után"
            />
          </div>

          <div class="field-group">
            <label class="label" for="exchangeTerms">Csere feltételei</label>
            <textarea
              id="exchangeTerms"
              v-model="exchangeTerms"
              class="input textarea"
              rows="3"
              placeholder="Pl.: EN-HU nyelvpár, legalább heti 1 alkalom"
            />
          </div>
        </template>

        <div class="field-group">
          <label class="label" for="password">Jelszó</label>
          <input id="password" v-model="password" class="input" type="password" placeholder="••••••••" required />
        </div>

        <div class="field-group">
          <label class="label" for="confirmPassword">Jelszó megerősítése</label>
          <input id="confirmPassword" v-model="confirmPassword" class="input" type="password" placeholder="••••••••" required />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button class="submit" type="submit" :disabled="loading">
          {{ loading ? 'Regisztrálás...' : 'Regisztrálás' }}
        </button>
      </form>

      <p class="switch-link">
        Már van fiókod?
        <router-link to="/login">Jelentkezz be!</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 32px 24px;
  background:
    radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.12) 0%, transparent 55%),
    radial-gradient(ellipse at 60% 85%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
    linear-gradient(135deg, #0f1623 0%, #161d2e 50%, #0f1420 100%);
}

.register-card {
  width: 100%;
  max-width: 420px;
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
  margin-bottom: 10px;
  display: block;
}

h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 8px 0 24px;
  color: #94a3b8;
  font-size: 0.93rem;
}

.register-form {
  display: grid;
  gap: 14px;
  text-align: left;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #cbd5e1;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.input {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 10px 13px;
  font-size: 0.93rem;
  color: #f1f5f9;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  width: 100%;
  box-sizing: border-box;
  font-family: inherit;
}

.input::placeholder {
  color: #475569;
}

.input:focus {
  border-color: rgba(99, 102, 241, 0.7);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  background: rgba(255, 255, 255, 0.09);
}

.input option {
  background: #1e2130;
  color: #f1f5f9;
}

.textarea {
  resize: vertical;
  min-height: 76px;
}

.error {
  margin: 0;
  color: #f87171;
  font-size: 0.88rem;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.25);
  border-radius: 8px;
  padding: 8px 12px;
  text-align: left;
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
  font-family: inherit;
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