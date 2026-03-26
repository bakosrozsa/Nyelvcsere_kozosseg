<script setup>
import { ref } from 'vue'
import axios from 'axios' // Ezt be kell importálnunk a kérésekhez!

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
    errorMessage.value = ''
    loading.value = true

    try {
        // 1. Összerakjuk az adatokat OAuth2 formátumba (mert a FastAPI ezt várja)
        const formData = new URLSearchParams()
        formData.append('username', email.value)
        formData.append('password', password.value)

        // 2. Elküldjük a POST kérést a backendnek
        const response = await axios.post('http://127.0.0.1:8000/login', formData)

        // 3. Ha sikeres (200 OK), a backend küld egy tokent. Ezt elmentjük a böngészőbe!
        const token = response.data.access_token
        localStorage.setItem('token', token)
        
        console.log('Sikeres bejelentkezés, token elmentve!')
        // IDE JÖN MAJD A TOVÁBBIRÁNYÍTÁS (pl. router.push('/dashboard'))

    } catch (error) {
        // Ha hibát kapunk (pl. 401 Unauthorized), szólunk a felhasználónak
        if (error.response && error.response.status === 401) {
            errorMessage.value = 'Hibás email vagy jelszó!'
        } else {
            errorMessage.value = 'Szerver hiba. Kérlek próbáld újra később.'
        }
        console.error('Login error:', error)
    } finally {
        loading.value = false
    }
}
</script>

<template>

    <main class="login-page">

        <section class="login-card">

            <h1 class="title">Bejelentkezes</h1>

            <p class="subtitle">Lepj be a Nyelvcsere kozossegbe.</p>



            <form class="login-form" @submit.prevent="handleLogin">

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



                <label class="label" for="password">Jelszo</label>

                <input

                    id="password"

                    v-model="password"

                    class="input"

                    type="password"

                    placeholder="••••••••"

                    autocomplete="current-password"

                    required

                />



                <p v-if="errorMessage" class="error">{{ errorMessage }}</p>



                <button class="submit" type="submit" :disabled="loading">

                    {{ loading ? 'Belepes...' : 'Belepes' }}

                </button>

            </form>

        </section>

    </main>

</template>



<style scoped>

.login-page {

    min-height: 100vh;

    display: grid;

    place-items: center;

    padding: 24px;

    background: linear-gradient(145deg, #f3f7fb 0%, #e7eef8 100%);

}



.login-card {

    width: 100%;

    max-width: 420px;

    background: #ffffff;

    border-radius: 16px;

    padding: 28px;

    box-shadow: 0 14px 40px rgba(14, 29, 52, 0.12);

}



.title {

    margin: 0;

    font-size: 1.75rem;

    color: #11233a;

}



.subtitle {

    margin: 8px 0 20px;

    color: #4d627b;

}



.login-form {

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

</style>