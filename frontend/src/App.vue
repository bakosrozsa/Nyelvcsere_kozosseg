<template>
  <div id="app">
    <header>
      <h1>Nyelvcsere Közösség</h1>
      <nav>
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
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isAuthenticated = ref(false)

watch(
  () => route.path,
  () => {
    isAuthenticated.value = !!localStorage.getItem('token')
  },
  { immediate: true }
)

const handleLogout = () => {
  localStorage.removeItem('token')
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

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 10px;
}

h1 {
  margin: 0;
  color: #2c3e50;
}

nav {
  display: flex;
  gap: 15px;
  align-items: center;
}

nav a {
  text-decoration: none;
  color: #2f7de1;
  font-weight: 500;
  transition: color 0.2s;
  cursor: pointer;
}

nav a:hover {
  color: #1653a2;
}

nav a.router-link-active {
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
</style>