<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Album {
  id: number
  title: string
  year: number
  created_at: string
  cover_url?: string
}

const recentAlbums = ref<Album[]>([])

// Tijdelijk hardcoded stats
const stats = {
  cds: 0,
  artists: 0,
  genres: 0
}

onMounted(async () => {
  try {
    // Haal albums op (limit 3, desc sort zou ideaal zijn maar API ondersteunt dat nog niet volledig qua sort params, we nemen gewoon de lijst)
    // TODO: Voeg sorting toe aan backend API
    const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/?limit=5`)
    if (response.ok) {
        const data = await response.json()
        recentAlbums.value = data
        stats.cds = data.length // Voor nu even dit als 'totaal'
    }
  } catch (e) {
    console.error(e)
  }
})
</script>

<template>
  <main class="w-full max-w-md mx-auto flex flex-col gap-6 p-4">
    
    <!-- Greeting -->
    <section class="flex flex-col gap-1 mt-2">
      <h2 class="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Goedemiddag, Eric</h2>
      <p class="text-slate-500 dark:text-slate-400 text-sm font-medium">Je collectie groeit gestaag.</p>
    </section>

    <!-- Stats -->
    <section class="grid grid-cols-3 gap-3">
      <div class="flex flex-col gap-1 rounded-2xl p-4 bg-white dark:bg-surface-dark shadow-sm border border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-2 text-primary mb-1">
          <span class="material-symbols-outlined text-[20px]">library_music</span>
        </div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">CDs</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ stats.cds }}</p>
      </div>
      <div class="flex flex-col gap-1 rounded-2xl p-4 bg-white dark:bg-surface-dark shadow-sm border border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-2 text-primary mb-1">
          <span class="material-symbols-outlined text-[20px]">mic</span>
        </div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Artiesten</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ stats.artists }}</p>
      </div>
      <div class="flex flex-col gap-1 rounded-2xl p-4 bg-white dark:bg-surface-dark shadow-sm border border-slate-100 dark:border-slate-800">
        <div class="flex items-center gap-2 text-primary mb-1">
          <span class="material-symbols-outlined text-[20px]">category</span>
        </div>
        <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Genres</p>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ stats.genres }}</p>
      </div>
    </section>

    <!-- Scan Action -->
    <section class="flex gap-3">
      <router-link to="/scan" class="flex-1 group relative flex items-center justify-between overflow-hidden rounded-2xl bg-primary p-5 shadow-lg shadow-primary/25 transition-all active:scale-[0.98]">
        <div class="relative z-10 flex flex-col items-start gap-1">
          <span class="text-lg font-bold text-white">Scan Barcode</span>
          <span class="text-xs font-medium text-blue-100">Snel toevoegen</span>
        </div>
        <div class="relative z-10 rounded-full bg-white/20 p-2 text-white">
          <span class="material-symbols-outlined text-[28px]">qr_code_scanner</span>
        </div>
        <!-- Decorative Glow -->
        <div class="absolute -right-4 -top-4 size-24 rounded-full bg-white/10 blur-xl"></div>
      </router-link>
    </section>

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

    <!-- Recently Added -->
    <div class="flex flex-col gap-4">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-bold leading-tight tracking-tight text-slate-900 dark:text-white">Recent Toegevoegd</h3>
        <button class="text-sm font-semibold text-primary hover:text-blue-600">Alles zien</button>
      </div>
      
      <div class="flex flex-col gap-3">
        <div v-for="album in recentAlbums" :key="album.id" class="group flex items-center gap-4 rounded-xl bg-white dark:bg-surface-dark p-3 shadow-sm border border-slate-100 dark:border-slate-800 active:scale-[0.99] transition-transform">
          <!-- Placeholder Cover -->
          <div class="relative size-16 shrink-0 overflow-hidden rounded-lg shadow-sm bg-gray-200 flex items-center justify-center">
            <img v-if="album.cover_url" :src="album.cover_url" class="w-full h-full object-cover" alt="Cover">
            <span v-else class="material-symbols-outlined text-gray-400">album</span>
          </div>
          
          <div class="flex flex-1 flex-col justify-center">
            <h4 class="font-bold text-slate-900 dark:text-white leading-tight line-clamp-1">{{ album.title }}</h4>
            <p class="text-sm font-medium text-slate-500 dark:text-slate-400">{{ album.year }}</p>
          </div>
          
          <div class="flex flex-col items-end gap-1">
            <span class="text-xs font-semibold text-slate-400">Recent</span>
            <div class="flex h-6 w-6 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-800 text-slate-400">
              <span class="material-symbols-outlined text-[16px]">chevron_right</span>
            </div>
          </div>
        </div>

        <div v-if="recentAlbums.length === 0" class="text-center text-slate-400 py-4">
            Nog geen albums. Begin met scannen!
        </div>
      </div>
    </div>

  </main>
</template>