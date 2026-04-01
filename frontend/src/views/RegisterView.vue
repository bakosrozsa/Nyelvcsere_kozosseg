<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

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

const API_BASE_URL = 'http://127.0.0.1:8000'

const fetchLanguages = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/languages`)
    if (!response.ok) {
      throw new Error('Nem sikerult a nyelveket betolteni.')
    }
    languages.value = await response.json()
  } catch (err) {
    error.value = err?.message || 'Hiba tortent a nyelvek lekerese soran.'
  }
}

const getAvailableRequestedLanguages = () => {
  if (!offeredLanguageId.value) {
    return languages.value
  }
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
      headers: {
        'Content-Type': 'application/json',
      },
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
      <h1>Regisztráció</h1>
      <p class="subtitle">Csatlakozz a Nyelvcsere közösséghez.</p>

      <form class="register-form" @submit.prevent="handleRegister">
        <label class="label" for="name">Név</label>
        <input
          id="name"
          v-model="name"
          class="input"
          type="text"
          placeholder="Teljes név"
          required
        />

        <label class="label" for="email">Email</label>
        <input
          id="email"
          v-model="email"
          class="input"
          type="email"
          placeholder="pelda@email.com"
          required
        />

        <label class="label" for="role">Szerep</label>
        <select v-model="role" class="input">
          <option value="student">Diák</option>
          <option value="mentor">Mentor</option>
        </select>

        <template v-if="role === 'student'">
          <label class="label" for="learningLanguage">Tanulni kívánt nyelv</label>
          <select id="learningLanguage" v-model="learningLanguageId" class="input" required>
            <option value="">Valassz nyelvet</option>
            <option v-for="language in languages" :key="`learning-${language.id}`" :value="language.id">
              {{ language.name }}
            </option>
          </select>
        </template>

        <template v-if="role === 'mentor'">
          <label class="label" for="offeredLanguage">Tanított nyelv</label>
          <select id="offeredLanguage" v-model="offeredLanguageId" class="input">
            <option value="">Valassz nyelvet</option>
            <option v-for="language in languages" :key="language.id" :value="language.id">
              {{ language.name }}
            </option>
          </select>

          <label class="label" for="requestedLanguage">Tanulni vágyott nyelv</label>
          <select id="requestedLanguage" v-model="requestedLanguageId" class="input">
            <option value="">Valassz nyelvet</option>
            <option v-for="language in getAvailableRequestedLanguages()" :key="`requested-${language.id}`" :value="language.id">
              {{ language.name }}
            </option>
          </select>

          <label class="label" for="availabilityDetails">Elérhetőség</label>
          <textarea
            id="availabilityDetails"
            v-model="availabilityDetails"
            class="input textarea"
            rows="3"
            placeholder="Pl.: Hetkoznap estenkent 18:00 utan, szombat delelott"
          />

          <label class="label" for="exchangeTerms">Csere feltételei</label>
          <textarea
            id="exchangeTerms"
            v-model="exchangeTerms"
            class="input textarea"
            rows="3"
            placeholder="Pl.: EN-HU nyelvpar, legalabb heti 1 alkalom, 60 perc"
          />
        </template>

        <label class="label" for="password">Jelszó</label>
        <input
          id="password"
          v-model="password"
          class="input"
          type="password"
          placeholder="••••••••"
          required
        />

        <label class="label" for="confirmPassword">Jelszó megerősítése</label>
        <input
          id="confirmPassword"
          v-model="confirmPassword"
          class="input"
          type="password"
          placeholder="••••••••"
          required
        />

        <p v-if="error" class="error">{{ error }}</p>

        <button class="submit" type="submit" :disabled="loading">
          {{ loading ? 'Regisztrálás...' : 'Regisztrálás' }}
        </button>

        <p class="login-link">
          Már van fiókod?
          <router-link to="/login">Jelentkezz be!</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
  background: linear-gradient(145deg, #f3f7fb 0%, #e7eef8 100%);
}

.register-card {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border-radius: 16px;
  padding: 28px;
  box-shadow: 0 14px 40px rgba(14, 29, 52, 0.12);
}

h1 {
  margin: 0;
  font-size: 1.75rem;
  color: #11233a;
}

.subtitle {
  margin: 8px 0 20px;
  color: #4d627b;
}

.register-form {
  display: grid;
  gap: 12px;
}

.label {
  font-size: 0.9rem;
  color: #2c3f59;
  font-weight: 600;
}

.input {
  border: 1px solid #c7d3e0;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input:focus {
  border-color: #2f7de1;
  box-shadow: 0 0 0 3px rgba(47, 125, 225, 0.15);
}

.textarea {
  resize: vertical;
  min-height: 72px;
}

.error {
  margin: 4px 0;
  color: #b42318;
  font-size: 0.9rem;
}

.submit {
  margin-top: 8px;
  border: none;
  border-radius: 10px;
  padding: 11px 14px;
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
  background: #1f67c8;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit:hover:not(:disabled) {
  background: #1653a2;
}

.submit:disabled {
  opacity: 0.7;
  cursor: wait;
}

.login-link {
  text-align: center;
  margin-top: 16px;
  color: #666;
}

.login-link a {
  color: #2f7de1;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
