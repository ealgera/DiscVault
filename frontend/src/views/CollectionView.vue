<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

interface Album {
  id: number
  title: string
  year?: number
  cover_url?: string
  artists: { name: string }[]
  tags?: { id: number, name: string, color: string }[]
  tracks?: { id: number, title: string, track_no: number, disc_no: number }[]
}

const router = useRouter()
const route = useRoute()

const searchQuery = ref(route.query.q?.toString() || '')
const searchFilter = ref(route.query.filter?.toString() || 'all')
const currentStatus = ref(route.query.status?.toString() || 'collection')
const sortBy = ref(route.query.sort?.toString() || 'artist')
const sortOrder = ref(route.query.order?.toString() || 'asc')
const albums = ref<Album[]>([])
const loading = ref(true)
const showSortMenu = ref(false)
let searchTimeout: number

async function fetchAlbums(query: string = '') {
    loading.value = true
    try {
        let url = `${import.meta.env.VITE_API_URL}/albums/?limit=1000&sort_by=${sortBy.value}&order=${sortOrder.value}&status=${currentStatus.value}`
        // Use current searchFilter if query exists, otherwise just list
        if (query) {
            url = `${import.meta.env.VITE_API_URL}/search?q=${encodeURIComponent(query)}&filter=${searchFilter.value}&sort_by=${sortBy.value}&order=${sortOrder.value}&status=${currentStatus.value}`
        }
        const response = await fetch(url)
        if (response.ok) {
            albums.value = await response.json()
        }
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
        window.scrollTo(0, 0)
    }
}

function updateQuery() {
    router.replace({ 
        query: { 
            q: searchQuery.value || undefined, 
            filter: searchFilter.value !== 'all' ? searchFilter.value : undefined,
            status: currentStatus.value !== 'collection' ? currentStatus.value : undefined,
            sort: sortBy.value !== 'created_at' ? sortBy.value : undefined,
            order: sortOrder.value !== 'desc' ? sortOrder.value : undefined
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
    if (filter === 'all') {
        searchQuery.value = ''
        sortBy.value = 'artist'
        sortOrder.value = 'asc'
    }
    searchFilter.value = filter
    updateQuery()
    fetchAlbums(searchQuery.value)
}

const sortOptions = [
    { id: 'title', label: 'Titel' },
    { id: 'artist', label: 'Artiest' },
    { id: 'year', label: 'Jaar (Release)' },
    { id: 'created_at', label: 'Datum Toegevoegd' }
]

const currentSortLabel = computed(() => {
    const option = sortOptions.find(o => o.id === sortBy.value)
    return option ? option.label : 'Datum'
})

function setSort(field: string) {
    if (sortBy.value === field) {
        sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
        sortBy.value = field
        sortOrder.value = 'asc' 
    }
    updateQuery()
    fetchAlbums(searchQuery.value)
}

function resolveCoverURL(url: string | undefined) {
    if (!url) return undefined
    if (url.startsWith('http')) return url
    const baseUrl = import.meta.env.VITE_API_URL.replace(/\/$/, '')
    const path = url.startsWith('/') ? url : `/${url}`
    // Using a fixed timestamp for collection view is usually enough to flush 
    // old caches from previous versions, or we could use Date.now() here too
    // but that might be expensive on scroll.
    return `${baseUrl}${path}?t=${Date.now()}`
}

function goToDetail(id: number) {
    router.push(`/albums/${id}`)
}

const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')

const alphabetMapping = computed(() => {
    const mapping: Record<string, number> = {}
    
    if (sortBy.value !== 'title' && sortBy.value !== 'artist') {
        return mapping
    }

    for (const album of albums.value) {
        let textToUse = ''
        if (sortBy.value === 'title') {
            textToUse = album.title
        } else if (sortBy.value === 'artist') {
            if (album.artists && album.artists.length > 0) {
                // The DB sorts by func.min(Artist.name), so we must find the alphabetically first artist
                const names = album.artists.map(a => a.name)
                names.sort()
                textToUse = names[0] || ''
            }
        }
        
        if (!textToUse) continue
        
        // Remove articles for sorting logic consistency only if the DB does it (but user manually handles this via 'Kast (De)')
        let cleanText = textToUse.trim().toUpperCase()
        
        const firstChar = cleanText.charAt(0)
        
        // If it's a letter and not mapped yet
        if (firstChar >= 'A' && firstChar <= 'Z' && !mapping[firstChar]) {
            mapping[firstChar] = album.id
        }
    }
    return mapping
})

function scrollToLetter(letter: string) {
    const targetId = alphabetMapping.value[letter]
    if (targetId) {
        const element = document.getElementById(`album-${targetId}`)
        if (element) {
            // Adjust scroll position dynamically based on actual header height
            const headerElement = document.getElementById('main-header')
            const headerOffset = headerElement ? headerElement.offsetHeight + 16 : 220 
            
            const elementPosition = element.getBoundingClientRect().top
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset
            
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            })
        }
    }
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
    <div id="main-header" class="sticky top-0 z-30 bg-gray-50/90 dark:bg-background-dark/90 backdrop-blur-md pt-4 pb-2">
      <!-- Status Tabs -->
      <div class="flex px-4 mb-4">
        <div class="flex p-1 bg-white dark:bg-surface-dark rounded-xl shadow-sm border border-slate-100 dark:border-slate-800 w-full">
            <button 
                @click="currentStatus = 'collection'; updateQuery(); fetchAlbums(searchQuery)"
                class="flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-2"
                :class="currentStatus === 'collection' ? 'bg-primary text-white shadow-md' : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800'"
            >
                <span class="material-symbols-outlined text-sm">album</span>
                Collectie
            </button>
            <button 
                @click="currentStatus = 'wishlist'; updateQuery(); fetchAlbums(searchQuery)"
                class="flex-1 py-2 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-2"
                :class="currentStatus === 'wishlist' ? 'bg-amber-500 text-white shadow-md' : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-800'"
            >
                <span class="material-symbols-outlined text-sm">auto_awesome</span>
                Wishlist
            </button>
        </div>
      </div>

      <div class="relative px-4 md:w-1/2 md:mx-auto">
        <span class="absolute inset-y-0 left-4 md:left-4 flex items-center pl-3">
          <span class="material-symbols-outlined text-slate-400">search</span>
        </span>
        <input 
          v-model="searchQuery" 
          @input="handleSearch"
          type="text" 
          placeholder="Zoek in je collectie..." 
          class="w-full pl-10 pr-10 py-3 rounded-xl border-none shadow-sm bg-white dark:bg-surface-dark text-slate-900 dark:text-white focus:ring-2 focus:ring-primary"
        >
        <!-- Clear Button -->
        <button 
          v-if="searchQuery"
          @click="searchQuery = ''; handleSearch()"
          class="absolute inset-y-0 right-4 flex items-center pr-3 group"
          title="Wissen"
        >
          <span class="material-symbols-outlined text-slate-300 hover:text-slate-500 transition-colors text-lg">close</span>
        </button>
      </div>

      <!-- Top Bar: Results Count & Sorting -->
      <div class="flex items-center justify-between px-4 mt-4">
        <div class="text-[10px] font-black uppercase text-slate-400 tracking-widest">
            {{ loading ? 'Zoeken...' : `${albums.length} ${currentStatus === 'wishlist' ? 'Items' : 'Albums'}` }}
        </div>
        
        <!-- Sorting Toggle -->
        <div class="relative shrink-0">
            <button 
                @click="showSortMenu = !showSortMenu"
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white dark:bg-surface-dark border border-slate-200 dark:border-slate-700 shadow-sm text-slate-600 dark:text-white hover:border-primary transition-colors"
            >
                <div class="flex flex-col items-center justify-center -space-y-2">
                    <span class="material-symbols-outlined text-[18px] leading-none">sort</span>
                </div>
                <span class="text-[10px] font-black uppercase tracking-wider">{{ currentSortLabel }}</span>
                <span class="material-symbols-outlined text-sm text-primary">
                    {{ sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward' }}
                </span>
            </button>

            <!-- Sort Menu Dropdown -->
            <div v-if="showSortMenu" class="absolute right-0 top-11 w-48 bg-white dark:bg-surface-dark rounded-2xl shadow-xl border border-slate-100 dark:border-slate-800 z-50 flex flex-col p-1.5 overflow-hidden">
                <div class="px-3 py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50 dark:border-slate-800 mb-1">
                    Sorteren op
                </div>
                <button 
                    v-for="s in sortOptions" 
                    :key="s.id"
                    @click="setSort(s.id)"
                    class="flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-all group"
                    :class="sortBy === s.id ? 'bg-primary/5 text-primary font-bold' : 'text-slate-600 dark:text-slate-400'"
                >
                    <span class="text-sm font-semibold">{{ s.label }}</span>
                    <div v-if="sortBy === s.id" class="flex items-center gap-1">
                        <span class="material-symbols-outlined text-sm animate-bounce-subtle">
                            {{ sortOrder === 'asc' ? 'arrow_upward' : 'arrow_downward' }}
                        </span>
                    </div>
                </button>
            </div>
        </div>
      </div>

      <!-- Filters Row -->
      <div class="flex items-center gap-2 mt-3 px-4 overflow-x-auto no-scrollbar py-1">
        <button 
            v-for="f in ['all', 'title', 'artist', 'track', 'genre', 'tag', 'media_type']" 
            :key="f"
            @click="setFilter(f)"
            class="px-3 py-1.5 rounded-full text-xs font-bold border transition-colors whitespace-nowrap shadow-sm"
            :class="searchFilter === f ? 'bg-primary text-white border-primary' : 'bg-white dark:bg-surface-dark text-slate-500 border-slate-200 dark:border-slate-700'"
        >
            {{ f === 'all' ? 'Alles' : f === 'track' ? 'Track' : f === 'media_type' ? 'Media' : f.charAt(0).toUpperCase() + f.slice(1) }}
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

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- A-Z Sidebar (Desktop only) -->
        <div 
          v-if="sortBy === 'title' || sortBy === 'artist'"
          class="fixed right-2 top-1/2 transform -translate-y-1/2 z-40 hidden sm:flex flex-col text-xs lg:text-sm font-bold bg-white/50 dark:bg-surface-dark/50 backdrop-blur-sm rounded-full py-2 px-1 border border-slate-200 dark:border-slate-800 shadow-sm"
        >
          <button
            v-for="letter in alphabet"
            :key="letter"
            @click="scrollToLetter(letter)"
            class="w-6 h-6 lg:w-7 lg:h-7 flex items-center justify-center rounded-full transition-colors my-[1px]"
            :class="alphabetMapping[letter] ? 'text-primary hover:bg-primary hover:text-white cursor-pointer' : 'text-slate-300 dark:text-slate-700 cursor-default'"
            :disabled="!alphabetMapping[letter]"
          >
            {{ letter }}
          </button>
        </div>

        <div 
          v-for="album in albums" 
          :key="album.id" 
          :id="'album-' + album.id"
          @click="goToDetail(album.id)"
          class="bg-white dark:bg-surface-dark border border-gray-100 dark:border-slate-800 p-4 rounded-lg shadow-sm flex items-center space-x-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition"
        >
          <div class="w-16 h-16 bg-gray-200 dark:bg-slate-800 rounded flex-shrink-0 overflow-hidden relative">
            <img 
              v-if="album.cover_url" 
              :src="resolveCoverURL(album.cover_url)" 
              alt="Cover" 
              class="w-full h-full object-cover"
              loading="lazy"
            >
            <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
              <span class="material-symbols-outlined">music_note</span>
            </div>
          </div>
          
          <div class="flex-1 min-w-0">
            <h3 class="font-bold text-slate-900 dark:text-white truncate">
                {{ album.title }} <span v-if="album.year" class="font-normal text-slate-400">({{ album.year }})</span>
            </h3>
            <p class="text-sm text-slate-500 truncate">
                {{ album.artists && album.artists.length ? album.artists.map(a => a.name).join(', ') : 'Onbekende artiest' }}
            </p> 
            
            <!-- Tags -->
            <div v-if="album.tags && album.tags.length" class="flex flex-wrap gap-1 mt-1">
                <span 
                    v-for="tag in album.tags" :key="tag.id"
                    class="px-1.5 py-0.5 rounded text-[9px] font-bold text-white uppercase tracking-tighter"
                    :style="{ backgroundColor: tag.color }"
                >
                    {{ tag.name }}
                </span>
            </div>

            <!-- Matching Tracks (only show if searching tracks or all and there's a hit) -->
            <div v-if="searchQuery && (searchFilter === 'all' || searchFilter === 'track')" class="mt-2 space-y-1">
                <div 
                    v-for="track in album.tracks?.filter(t => t.title.toLowerCase().includes(searchQuery.toLowerCase()))" 
                    :key="track.id"
                    class="text-[11px] text-primary bg-primary/5 px-2 py-0.5 rounded border border-primary/10 flex items-center gap-1"
                >
                    <span class="material-symbols-outlined text-[12px]">audiotrack</span>
                    <span class="font-bold text-slate-400 mr-1">{{ track.track_no }}.</span>
                    <span class="font-bold truncate">{{ track.title }}</span>
                    <span v-if="track.disc_no > 1" class="text-slate-400 ml-auto text-[9px] uppercase font-black tracking-tighter">CD {{ track.disc_no }}</span>
                </div>
            </div>
          </div>
          
          <span class="material-symbols-outlined text-slate-300">chevron_right</span>
        </div>
      </div>
    </div>
    
  </div>
</template>