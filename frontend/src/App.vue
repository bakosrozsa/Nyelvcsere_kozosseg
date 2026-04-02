<template>
  <div id="app">
    <header class="app-header">
      <h1 class="app-title">Nyelvcsere Közösség</h1>
      <nav class="app-nav">
        <router-link to="/">Kezdőoldal</router-link>
        <router-link to="/mentors">Mentorok</router-link>

        <template v-if="isAuthenticated">
          <router-link to="/dashboard">Felhasználók</router-link>
          <router-link to="/sessions">Foglalkozások</router-link>
          <router-link to="/profile">Profil</router-link>
          <a href="#" class="logout-btn" @click.prevent="handleLogout">Kijelentkezés</a>
        </template>

        <template v-else>
          <router-link to="/login">Belépés</router-link>
          <router-link to="/register">Regisztráció</router-link>
        </template>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const AUTH_LOGOUT_EVENT = 'auth:logout'

const isAuthenticated = ref(false)

watch(
  () => route.path,
  () => {
    isAuthenticated.value = !!localStorage.getItem('token')
  },
  { immediate: true }
)

const syncAuthState = () => {
  isAuthenticated.value = !!(localStorage.getItem('token') || localStorage.getItem('access_token'))
}

onMounted(() => {
  window.addEventListener(AUTH_LOGOUT_EVENT, syncAuthState)
  window.addEventListener('storage', syncAuthState)
})

onBeforeUnmount(() => {
  window.removeEventListener(AUTH_LOGOUT_EVENT, syncAuthState)
  window.removeEventListener('storage', syncAuthState)
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('access_token')
  window.dispatchEvent(new CustomEvent(AUTH_LOGOUT_EVENT, { detail: { reason: 'manual' } }))
  isAuthenticated.value = false
  router.push('/login')
}
</script>

<style>
#app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 12px;
}

.app-title {
  margin: 0;
  color: #2c3e50;
  font-size: clamp(1.2rem, 2.4vw, 1.8rem);
}

.app-nav {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.app-nav a {
  text-decoration: none;
  color: #2f7de1;
  font-weight: 500;
  transition: color 0.2s;
  cursor: pointer;
  white-space: nowrap;
}

.app-nav a:hover {
  color: #1653a2;
}

.app-nav a.router-link-active {
  color: #1653a2;
  border-bottom: 2px solid #1653a2;
  padding-bottom: 5px;
}

.logout-btn {
  color: #dc3545 !important;
}
.logout-btn:hover {
  color: #a71d2a !important;
}

main {
  min-height: 70vh;
}

@media (max-width: 820px) {
  #app {
    padding: 14px;
  }

  .app-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .app-nav {
    width: 100%;
    justify-content: flex-start;
    gap: 10px 14px;
  }
}

@media (max-width: 520px) {
  .app-nav a {
    padding: 6px 0;
    font-size: 0.95rem;
  }
}
</style>