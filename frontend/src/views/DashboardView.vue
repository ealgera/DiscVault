<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Album {
  id: number
  title: string
  year: number
  cover_url?: string
}

const stats = ref({
  albums: 0,
  artists: 0,
  genres: 0
})

const recentAlbums = ref<Album[]>([])
const error = ref('')

onMounted(async () => {
  try {
    // 1. Fetch Stats
    const statsRes = await fetch(`${import.meta.env.VITE_API_URL}/stats`)
    if (statsRes.ok) {
        stats.value = await statsRes.json()
    }

    // 2. Fetch Recent Albums
    const albumsRes = await fetch(`${import.meta.env.VITE_API_URL}/albums/?limit=5`)
    if (albumsRes.ok) {
        recentAlbums.value = await albumsRes.json()
    }
  } catch (e) {
    console.error(e)
    error.value = 'Kan data niet laden'
  }
})
</script>

<template>
  <main class="w-full max-w-md mx-auto flex flex-col gap-6 p-4">
    
    <div v-if="error" class="bg-red-100 text-red-700 p-2 rounded text-sm text-center">{{ error }}</div>

    <h2 class="text-3xl font-bold text-slate-900 dark:text-white">Goedemiddag, Eric</h2>
    
    <!-- Stats Grid -->
    <section class="grid grid-cols-3 gap-3">
      <div class="bg-white dark:bg-surface-dark p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex flex-col items-center">
        <span class="material-symbols-outlined text-primary mb-1">library_music</span>
        <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">CDs</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ stats.albums }}</p>
      </div>
      <div class="bg-white dark:bg-surface-dark p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex flex-col items-center">
        <span class="material-symbols-outlined text-primary mb-1">mic</span>
        <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Artiesten</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ stats.artists }}</p>
      </div>
      <div class="bg-white dark:bg-surface-dark p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex flex-col items-center">
        <span class="material-symbols-outlined text-primary mb-1">category</span>
        <p class="text-xs font-medium text-slate-500 uppercase tracking-wide">Genres</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ stats.genres }}</p>
      </div>
    </section>

    <!-- Scan Action -->
    <router-link to="/scan" class="group relative flex items-center justify-between overflow-hidden rounded-2xl bg-primary p-5 shadow-lg shadow-primary/25 transition-all active:scale-[0.98]">
        <div class="relative z-10 flex flex-col items-start gap-1">
          <span class="text-lg font-bold text-white">Scan Barcode</span>
          <span class="text-xs font-medium text-blue-100">Snel toevoegen</span>
        </div>
        <div class="relative z-10 rounded-full bg-white/20 p-2 text-white">
          <span class="material-symbols-outlined text-[28px]">qr_code_scanner</span>
        </div>
        <div class="absolute -right-4 -top-4 size-24 rounded-full bg-white/10 blur-xl"></div>
    </router-link>

    <!-- Quick Actions Grid -->
    <div class="flex flex-col gap-4">
      <h3 class="text-lg font-bold leading-tight tracking-tight text-slate-900 dark:text-white">Snelle Acties</h3>
      <div class="grid grid-cols-2 gap-3">
        <router-link to="/collection" class="flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-surface-dark p-4 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
          <div class="flex size-10 items-center justify-center rounded-full bg-blue-50 dark:bg-blue-900/30 text-primary">
            <span class="material-symbols-outlined">grid_view</span>
          </div>
          <span class="text-base font-bold text-slate-900 dark:text-white">Bladeren</span>
        </router-link>
        <button class="flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-surface-dark p-4 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
          <div class="flex size-10 items-center justify-center rounded-full bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400">
            <span class="material-symbols-outlined">analytics</span>
          </div>
          <span class="text-base font-bold text-slate-900 dark:text-white">Rapporten</span>
        </button>
        <button class="flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-surface-dark p-4 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
          <div class="flex size-10 items-center justify-center rounded-full bg-rose-50 dark:bg-rose-900/30 text-rose-500">
            <span class="material-symbols-outlined icon-filled">favorite</span>
          </div>
          <span class="text-base font-bold text-slate-900 dark:text-white">Favorieten</span>
        </button>
        <button class="flex items-center gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-surface-dark p-4 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
          <div class="flex size-10 items-center justify-center rounded-full bg-amber-50 dark:bg-amber-900/30 text-amber-500">
            <span class="material-symbols-outlined">bookmark</span>
          </div>
          <span class="text-base font-bold text-slate-900 dark:text-white">Wenslijst</span>
        </button>
      </div>
    </div>

    <!-- Recent List -->
    <div class="flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-bold leading-tight tracking-tight text-slate-900 dark:text-white">Recent Toegevoegd</h3>
        <router-link to="/collection" class="text-sm font-semibold text-primary hover:text-blue-600">Alles zien</router-link>
      </div>
      
      <div class="flex flex-col gap-3">
        <div 
            v-for="album in recentAlbums" 
            :key="album.id" 
            @click="$router.push(`/albums/${album.id}`)"
            class="group flex items-center gap-4 rounded-xl bg-white dark:bg-surface-dark p-3 shadow-sm border border-slate-100 dark:border-slate-800 active:scale-[0.99] transition-transform cursor-pointer"
        >
          <!-- Cover -->
          <div class="relative size-16 shrink-0 overflow-hidden rounded-lg shadow-sm bg-gray-200 flex items-center justify-center">
            <img v-if="album.cover_url" :src="album.cover_url" class="w-full h-full object-cover" alt="Cover">
            <span v-else class="material-symbols-outlined text-gray-400">album</span>
          </div>
          
          <div class="flex flex-1 flex-col justify-center min-w-0">
            <h4 class="font-bold text-slate-900 dark:text-white leading-tight truncate">{{ album.title }}</h4>
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ album.year }}</p>
          </div>
          
          <div class="flex flex-col items-end gap-1">
            <div class="flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400">
              <span class="material-symbols-outlined text-[16px]">chevron_right</span>
            </div>
          </div>
        </div>
        
        <div v-if="recentAlbums.length === 0 && !error" class="text-center text-slate-400 py-4 text-sm">
            Nog geen albums? Start met scannen!
        </div>
      </div>
    </div>

  </main>
</template>