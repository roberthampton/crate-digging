<script setup lang="ts">
import AlbumCrate from './components/AlbumCrate.vue';
</script>

<template>
  <div class="app">
    <header class="header">
      <h1 class="logo">
        <span class="logo-icon">📦</span>
        Crate Digging
      </h1>
      <p class="tagline">Discover your next favorite album</p>
    </header>
    
    <main class="main">
      <AlbumCrate />
    </main>
    
    <footer class="footer">
      <p>Flip through the crates • Find hidden gems • Expand your taste</p>
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #0d0d14;
}

.header {
  text-align: center;
  padding: 2rem 1rem 1rem;
}

.logo {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 2.8rem;
  color: #e8d5b7;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.logo-icon {
  font-size: 2.2rem;
}

.tagline {
  font-size: 1.1rem;
  color: #888;
  margin: 0.5rem 0 0;
  font-style: italic;
}

.main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer {
  text-align: center;
  padding: 1.5rem;
  color: #555;
  font-size: 0.9rem;
}

@media (max-width: 480px) {
  .logo {
    font-size: 2rem;
  }
  
  .tagline {
    font-size: 0.95rem;
  }
}
</style>
