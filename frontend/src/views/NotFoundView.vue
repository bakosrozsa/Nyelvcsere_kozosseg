<script setup>
</script>

<template>
  <div class="not-found">
    <h2>404 - Nem Található</h2>
    <p>Sajnos az oldal, amelyet keresel, nem létezik.</p>
    <router-link to="/">Vissza a kezdőoldalra</router-link>
  </div>
</template>

<style scoped>
.not-found {
  text-align: center;
  padding: 60px 20px;
}

.not-found h2 {
  color: #2c3e50;
  font-size: 2rem;
}

.not-found p {
  color: #666;
  margin-bottom: 20px;
}

.not-found a {
  color: #2f7de1;
  text-decoration: none;
  font-weight: 600;
}

.not-found a:hover {
  text-decoration: underline;
}
</style>
