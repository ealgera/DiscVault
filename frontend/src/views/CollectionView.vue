<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Tijdelijk de logic van HomeView hierheen verplaatst
interface Artist {
  id: number
  name: string
}

interface Album {
  id: number
  title: string
  year: number
  artists: Artist[]
  cover_url?: string
}

const albums = ref<Album[]>([])
const loading = ref(true)
const searchQuery = ref('')
let searchTimeout: any = null

async function fetchAlbums(query = '') {
  loading.value = true
  try {
    const url = query 
      ? `${import.meta.env.VITE_API_URL}/search?q=${encodeURIComponent(query)}`
      : `${import.meta.env.VITE_API_URL}/albums/`
    
    const response = await fetch(url)
    if (response.ok) {
        albums.value = await response.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    fetchAlbums(searchQuery.value)
  }, 300) // 300ms debounce
}

function goToDetail(id: number) {
    router.push(`/albums/${id}`)
}

onMounted(() => fetchAlbums())
</script>

<template>
  <div class="p-4 pb-20"> <!-- pb-20 voor ruimte boven de navbar -->
    <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-bold">Collectie</h1>
        <button class="bg-gray-200 p-2 rounded">Filter</button>
    </div>
    
    <!-- Zoekbalk -->
    <input 
      v-model="searchQuery"
      @input="handleSearch"
      type="search" 
      placeholder="Zoek op titel, artiest..." 
      class="w-full p-3 mb-4 border rounded-lg bg-white dark:bg-surface-dark dark:border-slate-700 dark:text-white border-gray-200 focus:outline-none focus:ring-2 focus:ring-primary" 
    />

    <div v-if="loading">Laden...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div 
        v-for="album in albums" 
        :key="album.id" 
        @click="goToDetail(album.id)"
        class="bg-white dark:bg-surface-dark border border-gray-100 dark:border-slate-800 p-4 rounded-lg shadow-sm flex items-center space-x-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition"
      >
        <div class="w-16 h-16 bg-gray-200 dark:bg-slate-800 rounded flex-shrink-0 overflow-hidden relative">
             <img v-if="album.cover_url" :src="album.cover_url" class="w-full h-full object-cover" alt="Cover">
             <span v-else class="material-symbols-outlined absolute inset-0 m-auto w-6 h-6 text-gray-400">album</span>
        </div> 
        <div class="min-w-0"> <!-- min-w-0 zorgt dat text truncate werkt in flex -->
            <h2 class="font-bold text-lg text-slate-900 dark:text-white truncate">{{ album.title }}</h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 truncate" v-for="artist in album.artists" :key="artist.id">{{ artist.name }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
