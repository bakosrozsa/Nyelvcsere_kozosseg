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
  min-height: 100vh;
}

main {
  backdrop-filter: blur(10px);
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 16px 20px;
  backdrop-filter: blur(15px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.app-title {
  margin: 0;
  color: #f1f5f9;
  font-size: clamp(1.2rem, 2.4vw, 1.8rem);
  font-weight: 700;
  letter-spacing: -0.5px;
}

.app-nav {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.app-nav a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.9rem;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 8px;
  transition: color 0.2s, background 0.2s;
}

.app-nav a:hover {
  color: #f1f5f9;
  background: rgba(99, 102, 241, 0.15);
}

.app-nav a.router-link-active {
  color: #818cf8;
  background: rgba(99, 102, 241, 0.1);
}

.logout-btn {
  color: #f87171 !important;
}

.logout-btn:hover {
  background: rgba(239, 68, 68, 0.1) !important;
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