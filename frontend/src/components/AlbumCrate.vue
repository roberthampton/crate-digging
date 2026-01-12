<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import type { Album, Genre } from '../types';
import { fetchRandomAlbums, fetchGenres } from '../api';

const albums = ref<Album[]>([]);
const currentIndex = ref(0);
const isLoading = ref(true);
const error = ref<string | null>(null);
const audioRef = ref<HTMLAudioElement | null>(null);
const isPlaying = ref(false);
const isDragging = ref(false);
const dragStartX = ref(0);
const dragOffset = ref(0);
const hasInteracted = ref(false);

// Genre filtering
const genres = ref<Genre[]>([]);
const selectedGenres = ref<number[]>([]);
const showGenreFilter = ref(false);

// Albums vs Singles filtering
const showOnlyAlbums = ref(false);

const currentAlbum = computed(() => albums.value[currentIndex.value]);
const prevAlbum = computed(() => albums.value[currentIndex.value - 1]);
const nextAlbum = computed(() => albums.value[currentIndex.value + 1]);

const selectedGenreNames = computed(() => {
  if (selectedGenres.value.length === 0) return 'All Genres';
  return genres.value
    .filter(g => selectedGenres.value.includes(g.id))
    .map(g => g.name)
    .join(', ');
});

const spotifyUrl = computed(() => {
  if (!currentAlbum.value) return '#';
  const query = `${currentAlbum.value.artist} ${currentAlbum.value.title}`;
  return `https://open.spotify.com/search/${encodeURIComponent(query)}`;
});

async function loadGenres() {
  try {
    genres.value = await fetchGenres();
  } catch (e) {
    console.error('Failed to load genres');
  }
}

function toggleGenre(genreId: number) {
  // Stop audio when changing filters
  stopPreview();
  
  const index = selectedGenres.value.indexOf(genreId);
  if (index === -1) {
    selectedGenres.value.push(genreId);
  } else {
    selectedGenres.value.splice(index, 1);
  }
}

function clearGenreFilter() {
  selectedGenres.value = [];
}

async function loadAlbums() {
  // Stop any playing audio when loading new albums
  stopPreview();
  
  isLoading.value = true;
  error.value = null;
  showGenreFilter.value = false;
  try {
    const genreIds = selectedGenres.value.length > 0 ? selectedGenres.value : undefined;
    const minTracks = showOnlyAlbums.value ? 2 : undefined; // 2+ tracks = album, 1 track = single
    const data = await fetchRandomAlbums(10, genreIds, minTracks);
    albums.value = data.albums;
    currentIndex.value = 0;
  } catch (e) {
    error.value = 'Failed to load albums. Make sure the backend is running.';
  } finally {
    isLoading.value = false;
  }
}

function playPreview() {
  if (!currentAlbum.value || !audioRef.value) return;
  hasInteracted.value = true;
  audioRef.value.src = currentAlbum.value.preview_url;
  audioRef.value.volume = 0.5;
  audioRef.value.play().catch(() => {
    // Autoplay blocked, user needs to interact first
  });
  isPlaying.value = true;
}

function stopPreview() {
  if (!audioRef.value) return;
  audioRef.value.pause();
  audioRef.value.currentTime = 0;
  isPlaying.value = false;
}

function goToNext() {
  if (currentIndex.value < albums.value.length - 1) {
    stopPreview();
    currentIndex.value++;
    if (hasInteracted.value) {
      setTimeout(playPreview, 150);
    }
  }
}

function goToPrev() {
  if (currentIndex.value > 0) {
    stopPreview();
    currentIndex.value--;
    if (hasInteracted.value) {
      setTimeout(playPreview, 150);
    }
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowRight') {
    goToNext();
  } else if (e.key === 'ArrowLeft') {
    goToPrev();
  } else if (e.key === ' ') {
    e.preventDefault();
    if (isPlaying.value) {
      stopPreview();
    } else {
      playPreview();
    }
  }
}

function handleDragStart(e: MouseEvent | TouchEvent) {
  isDragging.value = true;
  dragStartX.value = 'touches' in e ? e.touches[0].clientX : e.clientX;
  dragOffset.value = 0;
}

function handleDragMove(e: MouseEvent | TouchEvent) {
  if (!isDragging.value) return;
  const currentX = 'touches' in e ? e.touches[0].clientX : e.clientX;
  dragOffset.value = currentX - dragStartX.value;
}

function handleDragEnd() {
  if (!isDragging.value) return;
  isDragging.value = false;
  
  const threshold = 80;
  if (dragOffset.value > threshold) {
    goToPrev();
  } else if (dragOffset.value < -threshold) {
    goToNext();
  }
  
  dragOffset.value = 0;
}

onMounted(() => {
  loadGenres();
  loadAlbums();
  window.addEventListener('keydown', handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown);
  stopPreview();
});
</script>

<template>
  <div class="crate-container">
    <audio ref="audioRef" @ended="isPlaying = false"></audio>
    
    <div v-if="isLoading" class="loading">
      <div class="loading-spinner"></div>
      <p>Digging through the crates...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadAlbums" class="retry-btn">Try Again</button>
    </div>
    
    <div v-else-if="albums.length > 0" class="crate-viewer">
      <div class="album-stack"
           @mousedown="handleDragStart"
           @mousemove="handleDragMove"
           @mouseup="handleDragEnd"
           @mouseleave="handleDragEnd"
           @touchstart="handleDragStart"
           @touchmove="handleDragMove"
           @touchend="handleDragEnd">
        
        <!-- Previous album (behind) -->
        <div v-if="prevAlbum" 
             class="album-card prev"
             :style="{ transform: `translateX(${-320 + (isDragging ? dragOffset * 0.5 : 0)}px) scale(0.85) rotateY(15deg)` }">
          <img :src="prevAlbum.cover_url" :alt="prevAlbum.title" @error="(e) => (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300?text=No+Cover'" />
        </div>
        
        <!-- Current album (front) -->
        <div class="album-card current"
             :class="{ dragging: isDragging, playing: isPlaying }"
             :style="{ transform: `translateX(${isDragging ? dragOffset : 0}px) rotate(${isDragging ? dragOffset * 0.02 : 0}deg)` }"
             @click="isPlaying ? stopPreview() : playPreview()">
          <div class="album-vinyl" :class="{ spinning: isPlaying }"></div>
          <img :src="currentAlbum.cover_url" :alt="currentAlbum.title" @error="(e) => (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300?text=No+Cover'" />
          <div class="play-indicator" :class="{ active: isPlaying }">
            <span v-if="!isPlaying">▶</span>
            <span v-else>❚❚</span>
          </div>
        </div>
        
        <!-- Next album (behind) -->
        <div v-if="nextAlbum" 
             class="album-card next"
             :style="{ transform: `translateX(${320 + (isDragging ? dragOffset * 0.5 : 0)}px) scale(0.85) rotateY(-15deg)` }">
          <img :src="nextAlbum.cover_url" :alt="nextAlbum.title" @error="(e) => (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300?text=No+Cover'" />
        </div>
      </div>
      
      <div class="album-info">
        <h2 class="album-title">{{ currentAlbum.title }}</h2>
        <p class="album-artist">{{ currentAlbum.artist }}</p>
        <div class="album-meta">
          <span v-if="currentAlbum.year" class="album-year">{{ currentAlbum.year }}</span>
          <span 
            v-for="(genre, idx) in (currentAlbum.genres || (currentAlbum.genre ? [currentAlbum.genre] : []))" 
            :key="idx"
            class="album-genre">
            {{ genre }}
          </span>
          <span v-if="currentAlbum.nb_tracks" class="album-tracks">{{ currentAlbum.nb_tracks }} tracks</span>
        </div>
        <div class="external-links">
          <a 
            v-if="currentAlbum.deezer_link" 
            :href="currentAlbum.deezer_link" 
            target="_blank" 
            rel="noopener noreferrer"
            class="external-link deezer-link"
            @click.stop
          >
            Listen on Deezer →
          </a>
          <a 
            :href="spotifyUrl" 
            target="_blank" 
            rel="noopener noreferrer"
            class="external-link spotify-link"
            @click.stop
          >
            Listen on Spotify →
          </a>
        </div>
      </div>
      
      <div class="controls">
        <button 
          @click="goToPrev" 
          :disabled="currentIndex === 0"
          class="nav-btn prev-btn">
          ← Prev
        </button>
        
        <div class="progress-indicator">
          {{ currentIndex + 1 }} / {{ albums.length }}
        </div>
        
        <button 
          @click="goToNext" 
          :disabled="currentIndex === albums.length - 1"
          class="nav-btn next-btn">
          Next →
        </button>
      </div>
      
      <div class="action-buttons">
        <button @click="loadAlbums" class="shuffle-btn">
          🔀 Shuffle New Crate
        </button>
        
        <div class="release-type-selector">
          <label for="release-type" class="release-type-label">Release Type:</label>
          <select 
            id="release-type"
            v-model="showOnlyAlbums" 
            @change="loadAlbums()"
            class="release-type-dropdown">
            <option :value="false">📀 All Releases (Albums + Singles)</option>
            <option :value="true">💿 Albums Only (2+ tracks)</option>
          </select>
        </div>
        
        <button @click="showGenreFilter = !showGenreFilter" class="filter-btn" :class="{ active: selectedGenres.length > 0 }">
          🎸 {{ selectedGenres.length > 0 ? `${selectedGenres.length} Genre${selectedGenres.length > 1 ? 's' : ''}` : 'Filter' }}
        </button>
      </div>
      
      <div v-if="showGenreFilter" class="genre-filter">
        <div class="genre-filter-header">
          <span>Filter by Genre</span>
          <button v-if="selectedGenres.length > 0" @click="clearGenreFilter" class="clear-btn">Clear All</button>
        </div>
        <div class="genre-grid">
          <button 
            v-for="genre in genres" 
            :key="genre.id"
            @click="toggleGenre(genre.id)"
            class="genre-chip"
            :class="{ selected: selectedGenres.includes(genre.id) }"
          >
            {{ genre.name }}
          </button>
        </div>
        <button @click="loadAlbums" class="apply-filter-btn">
          Apply & Shuffle
        </button>
      </div>
      
      <p v-if="selectedGenres.length > 0 || showOnlyAlbums" class="active-filter-hint">
        <span v-if="showOnlyAlbums">📀 Albums Only</span>
        <span v-if="showOnlyAlbums && selectedGenres.length > 0"> • </span>
        <span v-if="selectedGenres.length > 0">Filtering: {{ selectedGenreNames }}</span>
      </p>
      
      <p class="hint">Click album to play/pause • Drag or use arrow keys to browse • Space to toggle</p>
      
      <div class="powered-by">
        <span>Powered by</span>
        <svg class="deezer-logo" viewBox="0 0 500 200" fill="currentColor">
          <path d="M0 150.3V130h54.6v20.3H0zm0-34.3V95.7h54.6V116H0zm0-34.3V61.4h54.6v20.3H0zm0-34.3V27.1h54.6v20.3H0zM66.5 150.3V130H121v20.3H66.5zm0-34.3V95.7H121V116H66.5zM133 150.3V130h54.5v20.3H133zm0-34.3V95.7h54.5V116H133zm0-34.3V61.4h54.5v20.3H133zm0-34.3V27.1h54.5v20.3H133zM199.4 150.3V130h54.6v20.3h-54.6zm0-34.3V95.7h54.6V116h-54.6zm0-34.3V61.4h54.6v20.3h-54.6zM265.9 150.3V130h54.6v20.3h-54.6zm0-34.3V95.7h54.6V116h-54.6zm0-34.3V61.4h54.6v20.3h-54.6zm0-34.3V27.1h54.6v20.3h-54.6z"/>
        </svg>
      </div>
    </div>
  </div>
</template>

<style scoped>
.crate-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 2rem;
  user-select: none;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(90, 138, 90, 0.2);
  border-top-color: #5a8a5a;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading p {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 1.4rem;
  color: #d4d0c4;
  font-style: italic;
}

.error {
  text-align: center;
}

.error p {
  color: #8b6f5f;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.retry-btn {
  background: linear-gradient(135deg, #5a8a5a, #6b8b6b);
  color: #f5f5f0;
  border: none;
  padding: 0.8rem 2rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 25px rgba(90, 138, 90, 0.4);
}

.crate-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  max-width: 600px;
}

.album-stack {
  position: relative;
  width: 300px;
  height: 300px;
  perspective: 1000px;
  cursor: grab;
}

.album-stack:active {
  cursor: grabbing;
}

.album-card {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 8px;
  overflow: visible;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.3s ease;
  transform-style: preserve-3d;
}

.album-card.dragging {
  transition: none;
}

.album-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
  position: relative;
  z-index: 2;
}

.album-card.prev,
.album-card.next {
  opacity: 0.6;
  filter: brightness(0.7);
}

.album-card.current {
  z-index: 10;
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6), 0 0 0 2px rgba(90, 138, 90, 0.3);
}

.album-card.current:hover {
  box-shadow: 0 30px 90px rgba(0, 0, 0, 0.7), 0 0 0 3px rgba(90, 138, 90, 0.5);
}

.album-card.current.playing {
  box-shadow: 0 25px 80px rgba(0, 0, 0, 0.6), 0 0 30px rgba(90, 138, 90, 0.6);
}

.album-vinyl {
  position: absolute;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle at center,
    #1a1a1a 0%,
    #1a1a1a 15%,
    #2a2a2a 15%,
    #1a1a1a 17%,
    #2a2a2a 30%,
    #1a1a1a 32%,
    #2a2a2a 50%,
    #1a1a1a 52%,
    #2a2a2a 70%,
    #1a1a1a 72%,
    #2a2a2a 100%
  );
  border-radius: 50%;
  top: 10px;
  left: 150px;
  z-index: 1;
  transition: left 0.5s ease;
  box-shadow: inset 0 0 30px rgba(0,0,0,0.8), 0 0 20px rgba(0,0,0,0.5);
}

.album-vinyl::before {
  content: '';
  position: absolute;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #5a8a5a, #6b8b6b);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 10px rgba(90, 138, 90, 0.5);
}

.album-vinyl::after {
  content: '';
  position: absolute;
  width: 10px;
  height: 10px;
  background: #1a1a1a;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.album-card.current.playing .album-vinyl {
  left: 200px;
}

.album-vinyl.spinning {
  animation: vinyl-spin 2s linear infinite;
}

@keyframes vinyl-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.play-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80px;
  height: 80px;
  background: rgba(0, 0, 0, 0.7);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: #5a8a5a;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 3;
  backdrop-filter: blur(5px);
}

.album-card.current:hover .play-indicator {
  opacity: 1;
}

.play-indicator.active {
  opacity: 1;
  background: rgba(90, 138, 90, 0.2);
}

.album-info {
  text-align: center;
  padding: 1rem;
}

.album-title {
  font-family: 'Instrument Serif', Georgia, serif;
  font-size: 2rem;
  color: #d4d0c4;
  margin: 0 0 0.5rem 0;
  line-height: 1.2;
}

.album-artist {
  font-size: 1.2rem;
  color: #5a8a5a;
  margin: 0 0 0.8rem 0;
  font-weight: 500;
}

.album-meta {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.album-year,
.album-genre,
.album-tracks {
  background: rgba(90, 138, 90, 0.15);
  color: #d4d0c4;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.85rem;
  border: 1px solid rgba(90, 138, 90, 0.3);
}

.external-links {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.external-link {
  display: inline-block;
  color: #5a8a5a;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border: 1px solid rgba(90, 138, 90, 0.4);
  border-radius: 20px;
  transition: all 0.3s ease;
}

.external-link:hover {
  background: rgba(90, 138, 90, 0.2);
  border-color: #5a8a5a;
}

.spotify-link {
  color: #1db954;
  border-color: rgba(29, 185, 84, 0.4);
}

.spotify-link:hover {
  background: rgba(29, 185, 84, 0.2);
  border-color: #1db954;
}

.controls {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.nav-btn {
  background: transparent;
  border: 2px solid #5a8a5a;
  color: #5a8a5a;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.nav-btn:hover:not(:disabled) {
  background: #5a8a5a;
  color: #f5f5f0;
  transform: scale(1.05);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.progress-indicator {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1rem;
  color: #a0a0a0;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.5rem 1rem;
  border-radius: 20px;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.shuffle-btn {
  background: linear-gradient(135deg, #5a8a5a, #6b8b6b);
  color: #f5f5f0;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 700;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.shuffle-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(90, 138, 90, 0.4);
}

.filter-btn {
  background: transparent;
  border: 2px solid #5a8a5a;
  color: #5a8a5a;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  background: rgba(90, 138, 90, 0.1);
}

.filter-btn.active {
  background: rgba(90, 138, 90, 0.2);
  border-color: #6b8b6b;
}

.release-type-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.release-type-label {
  color: #d4d0c4;
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
}

.release-type-dropdown {
  background: rgba(90, 138, 90, 0.1);
  border: 2px solid #5a8a5a;
  color: #d4d0c4;
  padding: 0.8rem 1.2rem;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%235a8a5a' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  padding-right: 2.5rem;
}

.release-type-dropdown:hover {
  background-color: rgba(90, 138, 90, 0.2);
  border-color: #6b8b6b;
}

.release-type-dropdown:focus {
  outline: none;
  border-color: #6b8b6b;
  box-shadow: 0 0 0 3px rgba(90, 138, 90, 0.2);
}

.genre-filter {
  background: rgba(61, 46, 38, 0.95);
  border: 1px solid rgba(90, 138, 90, 0.3);
  border-radius: 16px;
  padding: 1.5rem;
  margin-top: 1rem;
  width: 100%;
  max-width: 500px;
  backdrop-filter: blur(10px);
}

.genre-filter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  color: #d4d0c4;
  font-weight: 600;
}

.clear-btn {
  background: transparent;
  border: none;
  color: #5a8a5a;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.3rem 0.6rem;
  border-radius: 12px;
  transition: background 0.2s ease;
}

.clear-btn:hover {
  background: rgba(90, 138, 90, 0.2);
}

.genre-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.genre-chip {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(212, 208, 196, 0.15);
  color: #8b6f5f;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.genre-chip:hover {
  border-color: rgba(90, 138, 90, 0.5);
  color: #d4d0c4;
}

.genre-chip.selected {
  background: rgba(90, 138, 90, 0.25);
  border-color: #5a8a5a;
  color: #5a8a5a;
}

.apply-filter-btn {
  width: 100%;
  background: linear-gradient(135deg, #5a8a5a, #6b8b6b);
  color: #f5f5f0;
  border: none;
  padding: 0.8rem 1.5rem;
  font-size: 1rem;
  font-weight: 700;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.apply-filter-btn:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 20px rgba(90, 138, 90, 0.3);
}

.active-filter-hint {
  font-size: 0.85rem;
  color: #5a8a5a;
  text-align: center;
  margin-top: 0.8rem;
  padding: 0.4rem 1rem;
  background: rgba(90, 138, 90, 0.1);
  border-radius: 15px;
  display: inline-block;
}

.hint {
  font-size: 0.85rem;
  color: #8b6f5f;
  text-align: center;
  margin-top: 1rem;
}

.powered-by {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  color: #8b6f5f;
  font-size: 0.8rem;
}

.deezer-logo {
  width: 60px;
  height: 24px;
  color: #8b6f5f;
  transition: color 0.3s ease;
}

.powered-by:hover .deezer-logo {
  color: #5a8a5a;
}

@media (max-width: 480px) {
  .album-stack {
    width: 250px;
    height: 250px;
  }
  
  .album-card {
    width: 250px;
    height: 250px;
  }
  
  .album-vinyl {
    width: 230px;
    height: 230px;
  }
  
  .album-title {
    font-size: 1.5rem;
  }
  
  .controls {
    gap: 1rem;
  }
  
  .nav-btn {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }
}
</style>

