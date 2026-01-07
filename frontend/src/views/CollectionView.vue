<script setup lang="ts">
import { ref, onMounted } from 'vue'

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

onMounted(async () => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/`)
    if (response.ok) {
        albums.value = await response.json()
    }
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="p-4 pb-20"> <!-- pb-20 voor ruimte boven de navbar -->
    <div class="flex justify-between items-center mb-4">
        <h1 class="text-2xl font-bold">Collectie</h1>
        <button class="bg-gray-200 p-2 rounded">Filter</button>
    </div>
    
    <!-- Zoekbalk placeholder -->
    <input type="search" placeholder="Zoek op titel, artiest..." class="w-full p-3 mb-4 border rounded-lg bg-gray-50" />

    <div v-if="loading">Laden...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-for="album in albums" :key="album.id" class="bg-white p-4 rounded-lg shadow flex items-center space-x-4">
        <div class="w-16 h-16 bg-gray-200 rounded flex-shrink-0 overflow-hidden relative">
             <img v-if="album.cover_url" :src="album.cover_url" class="w-full h-full object-cover" alt="Cover">
             <span v-else class="material-symbols-outlined absolute inset-0 m-auto w-6 h-6 text-gray-400">album</span>
        </div> 
        <div>
            <h2 class="font-bold text-lg">{{ album.title }}</h2>
            <p class="text-sm text-gray-600" v-for="artist in album.artists" :key="artist.id">{{ artist.name }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
