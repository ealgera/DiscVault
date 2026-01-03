<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Artist {
  id: number
  name: string
}

interface Album {
  id: number
  title: string
  year: number
  artists: Artist[]
}

const albums = ref<Album[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/albums/')
    if (!response.ok) throw new Error('Failed to fetch albums')
    albums.value = await response.json()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <main class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-slate-800">DiscVault Collectie</h1>

    <div v-if="loading" class="text-gray-500">Laden...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="album in albums" :key="album.id" class="bg-white border rounded-lg shadow p-4 hover:shadow-lg transition">
        <h2 class="text-xl font-semibold">{{ album.title }}</h2>
        <p class="text-gray-600">
          <span v-for="(artist, index) in album.artists" :key="artist.id">
            {{ artist.name }}<span v-if="index < album.artists.length - 1">, </span>
          </span>
        </p>
        <p class="text-sm text-gray-400 mt-2">{{ album.year }}</p>
      </div>
    </div>
  </main>
</template>