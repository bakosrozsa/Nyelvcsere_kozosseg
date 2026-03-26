<template>
  <div id="app">
    <header>
      <h1>Nyelvcsere Közösség</h1>
      <nav>
        <router-link to="/">Kezdőoldal</router-link>
        <router-link to="/dashboard">Felhasználók</router-link>
        <router-link to="/mentors">Mentorok</router-link>
        <router-link to="/profile">Profil</router-link>
        <router-link to="/login">Kijelentkezés</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
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
}

nav a {
  text-decoration: none;
  color: #2f7de1;
  font-weight: 500;
  transition: color 0.2s;
}

nav a:hover {
  color: #1653a2;
}

nav a.router-link-active {
  color: #1653a2;
  border-bottom: 2px solid #1653a2;
  padding-bottom: 5px;
}

main {
  min-height: 70vh;
}
</style>