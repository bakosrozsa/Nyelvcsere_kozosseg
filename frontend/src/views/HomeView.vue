<script setup>
import { ref, onMounted } from 'vue'

const isAuthenticated = ref(false)

onMounted(() => {
  isAuthenticated.value = !!localStorage.getItem('token')
})
</script>

<template>
  <section class="home-page">
    <div class="hero">
      <p class="eyebrow">Nyelvcsere Közösség</p>
      <h2>Találd meg a megfelelő mentort, és fejlődj valós beszélgetésekkel</h2>
      <p class="lead">
        A platform segít összekötni tanulókat és mentorokat, hogy a nyelvtanulás ne csak elmélet,
        hanem rendszeres, gyakorlati kommunikáció legyen.
      </p>

      <div class="actions">
        <router-link class="btn primary" to="/mentors">Mentorok megtekintése</router-link>
        
        <router-link v-if="isAuthenticated" class="btn ghost" to="/sessions">Foglalkozások kezelése</router-link>
        
        <router-link v-else class="btn ghost" to="/register">Csatlakozás ingyen</router-link>
      </div>
    </div>

    <div class="stats-grid">
      <article class="stat-card">
        <h3>Mentorok</h3>
        <p>Nézd meg, kik tanítanak, milyen nyelveket vállalnak, és milyen formában segítenek.</p>
      </article>
      <article class="stat-card">
        <h3>Foglalkozások</h3>
        <p>Új alkalmak rögzítése, időpont-módosítás, törlés és állapotkövetés egy helyen.</p>
      </article>
      <article class="stat-card">
        <h3>Fejlődés</h3>
        <p>A rendszeres beszédgyakorlat segít magabiztosabbá válni és gyorsabban haladni.</p>
      </article>
    </div>

    <div class="info-panel">
      <h3>Hogyan kezdj neki?</h3>
      <div class="steps-grid">
        <article class="step-card">
          <span class="step-index">1</span>
          <p>Jelentkezz be vagy regisztrálj egy új fiókot.</p>
        </article>
        <article class="step-card">
          <span class="step-index">2</span>
          <p>Válassz mentort a céljaidnak megfelelően.</p>
        </article>
        <article class="step-card">
          <span class="step-index">3</span>
          <p>Ütemezz egy foglalkozást, majd kövesd a haladást a Foglalkozások oldalon.</p>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home-page {
  display: grid;
  gap: 24px;
  padding: 20px 0 28px;
}

.hero {
  background: linear-gradient(140deg, #f8fbff 0%, #ecf3ff 100%);
  border: 1px solid #d8e4f3;
  border-radius: 16px;
  padding: 26px;
}

.eyebrow {
  margin: 0;
  color: #2f6fb8;
  font-weight: 700;
  font-size: 0.9rem;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.hero h2 {
  margin: 8px 0 12px;
  color: #132941;
  font-size: clamp(1.4rem, 3.2vw, 2rem);
  line-height: 1.25;
}

.lead {
  margin: 0 auto;
  color: #44596f;
  line-height: 1.6;
  max-width: 70ch;
  text-align: center;
}

.actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 18px;
  justify-content: center;
}

.btn {
  text-decoration: none;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

.btn.primary {
  background: #1f67c8;
  color: #ffffff;
  box-shadow: 0 6px 14px rgba(31, 103, 200, 0.24);
}

.btn.ghost {
  background: #ffffff;
  color: #1f67c8;
  border: 1px solid #8db2e4;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  background: #ffffff;
  border: 1px solid #dde6f1;
  border-radius: 12px;
  padding: 16px;
}

.stat-card h3 {
  margin: 0 0 8px;
  color: #1e354d;
  font-size: 1.05rem;
}

.stat-card p {
  margin: 0;
  color: #4f6378;
  line-height: 1.5;
}

.info-panel {
  border: 1px solid #dde6f1;
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
}

.info-panel h3 {
  margin: 0 0 16px;
  color: #1e354d;
  text-align: center;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.step-card {
  border: 1px solid #dbe6f3;
  border-radius: 10px;
  padding: 14px;
  background: #f8fbff;
}

.step-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: #1f67c8;
  color: #ffffff;
  font-weight: 700;
  margin-bottom: 8px;
}

.step-card p {
  margin: 0;
  color: #4f6378;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .steps-grid {
    grid-template-columns: 1fr;
  }

  .hero {
    padding: 20px;
  }
}
</style>