<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

interface Album {
  id: number
  title: string
  cover_url?: string
}

const router = useRouter()
const route = useRoute()

const searchQuery = ref(route.query.q?.toString() || '')
const searchFilter = ref(route.query.filter?.toString() || 'all')
const albums = ref<Album[]>([])
const loading = ref(true)
let searchTimeout: number

async function fetchAlbums(query: string = '') {
    loading.value = true
    try {
        let url = `${import.meta.env.VITE_API_URL}/albums/`
        // Use current searchFilter if query exists, otherwise just list
        if (query) {
            url = `${import.meta.env.VITE_API_URL}/search?q=${encodeURIComponent(query)}&filter=${searchFilter.value}`
        }
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

function updateQuery() {
    router.replace({ 
        query: { 
            q: searchQuery.value || undefined, 
            filter: searchFilter.value !== 'all' ? searchFilter.value : undefined 
        } 
    })
}

function handleSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    updateQuery()
    fetchAlbums(searchQuery.value)
  }, 300) // 300ms debounce
}

function setFilter(filter: string) {
    searchFilter.value = filter
    updateQuery()
    if (searchQuery.value) {
        fetchAlbums(searchQuery.value)
    }
}

function goToDetail(id: number) {
    router.push(`/albums/${id}`)
}

onMounted(() => {
    // If URL has query, fetch immediately
    if (searchQuery.value) {
        fetchAlbums(searchQuery.value)
    } else {
        fetchAlbums()
    }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-background-dark pb-24">
    
    <!-- HEADER -->
    <div class="sticky top-0 z-30 bg-gray-50/90 dark:bg-background-dark/90 backdrop-blur-md py-4">
      <div class="relative px-4">
        <span class="absolute inset-y-0 left-4 flex items-center pl-3">
          <span class="material-symbols-outlined text-slate-400">search</span>
        </span>
        <input 
          v-model="searchQuery" 
          @input="handleSearch"
          type="text" 
          placeholder="Zoek in je collectie..." 
          class="w-full pl-10 pr-4 py-3 rounded-xl border-none shadow-sm bg-white dark:bg-surface-dark text-slate-900 dark:text-white focus:ring-2 focus:ring-primary"
        >
      </div>

      <!-- Filters -->
      <div class="flex gap-2 mt-3 overflow-x-auto pb-1 no-scrollbar px-4">
        <button 
            v-for="f in ['all', 'title', 'artist', 'genre', 'tag']" 
            :key="f"
            @click="setFilter(f)"
            class="px-3 py-1 rounded-full text-xs font-bold border transition-colors whitespace-nowrap"
            :class="searchFilter === f ? 'bg-primary text-white border-primary' : 'bg-white dark:bg-surface-dark text-slate-500 border-slate-200 dark:border-slate-700'"
        >
            {{ f === 'all' ? 'Alles' : f.charAt(0).toUpperCase() + f.slice(1) }}
        </button>
      </div>
    </div>

    <!-- CONTENT -->
    <div class="px-4">
      <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>

      <div v-else-if="albums.length === 0" class="flex flex-col items-center justify-center py-20 text-slate-400">
        <span class="material-symbols-outlined text-6xl mb-4 opacity-50">album</span>
        <p>Geen albums gevonden.</p>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="album in albums" 
          :key="album.id" 
          @click="goToDetail(album.id)"
          class="bg-white dark:bg-surface-dark border border-gray-100 dark:border-slate-800 p-4 rounded-lg shadow-sm flex items-center space-x-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition"
        >
          <div class="w-16 h-16 bg-gray-200 dark:bg-slate-800 rounded flex-shrink-0 overflow-hidden relative">
            <img 
              v-if="album.cover_url" 
              :src="album.cover_url" 
              alt="Cover" 
              class="w-full h-full object-cover"
              loading="lazy"
            >
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
              <span class="material-symbols-outlined">music_note</span>
            </div>
          </div>
          
          <div class="flex-1 min-w-0">
            <h3 class="font-bold text-slate-900 dark:text-white truncate">{{ album.title }}</h3>
            <!-- We could add artist here if we had it in the list response, but it requires backend update to include artists in list view efficiently -->
            <p class="text-sm text-slate-500 truncate">Album</p> 
          </div>
          
          <span class="material-symbols-outlined text-slate-300">chevron_right</span>
        </div>
      </div>
    </div>
    
  </div>
</template>