<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const stats = ref<any>({})
const loading = ref(true)
const error = ref('')

async function fetchStats() {
    loading.value = true
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/reports/stats`)
        if (response.ok) {
            stats.value = await response.json()
        } else {
            error.value = 'Kon rapportstatistieken niet laden'
        }
    } catch (e) {
        error.value = 'Fout bij verbinden met server'
    } finally {
        loading.value = false
    }
}

onMounted(fetchStats)

const metadataReports = [
    { key: 'unused_genres', title: 'Ongebruikte Genres', icon: 'category', color: 'text-blue-500', bg: 'bg-blue-50' },
    { key: 'low_usage_genres', title: 'Weinig gebruikte Genres', icon: 'category', color: 'text-blue-400', bg: 'bg-blue-50' },
    { key: 'unused_tags', title: 'Ongebruikte Tags', icon: 'tag', color: 'text-purple-500', bg: 'bg-purple-50' },
    { key: 'low_usage_tags', title: 'Weinig gebruikte Tags', icon: 'tag', color: 'text-purple-400', bg: 'bg-purple-50' },
    { key: 'unused_artists', title: 'Artiesten zonder album', icon: 'mic', color: 'text-amber-500', bg: 'bg-amber-50' },
]

const albumReports = [
    { key: 'missing_covers', title: 'Zonder Hoes', icon: 'image_not_supported' },
    { key: 'missing_tracks', title: 'Zonder Tracks', icon: 'grid_view' },
    { key: 'missing_year', title: 'Zonder Jaar', icon: 'calendar_today' },
    { key: 'missing_location', title: 'Zonder Locatie', icon: 'shelves' },
    { key: 'missing_media', title: 'Zonder Media type', icon: 'album' },
    { key: 'missing_catalog', title: 'Zonder Catalogus #', icon: 'barcode' },
]
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-background-dark pb-20">
    <div class="sticky top-0 z-40 bg-gray-50/90 dark:bg-background-dark/90 backdrop-blur-md p-4 flex items-center gap-4">
        <button @click="router.back()" class="flex items-center text-primary font-bold gap-1 hover:text-blue-700 transition">
            <span class="material-symbols-outlined text-xl">arrow_back_ios_new</span>
            Terug
        </button>
        <h1 class="text-xl font-black text-slate-900 dark:text-white">Rapporten</h1>
    </div>

    <div class="p-6 max-w-lg mx-auto space-y-8">
        
        <div v-if="loading" class="flex justify-center py-20">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-xl font-bold text-center">
            {{ error }}
        </div>

        <template v-else>
            <!-- Metadata Section -->
            <section class="space-y-4">
                <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 px-1">Metadata Opschonen</h3>
                <div class="grid grid-cols-1 gap-3">
                    <button 
                        v-for="rep in metadataReports" 
                        :key="rep.key"
                        @click="router.push(`/reports/${rep.key}`)"
                        class="flex items-center justify-between bg-white dark:bg-surface-dark p-4 rounded-2xl border border-slate-100 dark:border-slate-800 hover:shadow-md transition group active:scale-[0.98]"
                    >
                        <div class="flex items-center gap-4">
                            <div class="size-10 rounded-full flex items-center justify-center" :class="rep.bg">
                                <span class="material-symbols-outlined" :class="rep.color">{{ rep.icon }}</span>
                            </div>
                            <span class="font-bold text-slate-700 dark:text-slate-200">{{ rep.title }}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <span class="text-lg font-black" :class="stats[rep.key] > 0 ? 'text-primary' : 'text-slate-300'">{{ stats[rep.key] }}</span>
                            <span class="material-symbols-outlined text-slate-300 group-hover:translate-x-1 transition-transform">chevron_right</span>
                        </div>
                    </button>
                </div>
            </section>

            <!-- Albums Section -->
            <section class="space-y-4">
                <h3 class="text-xs font-black uppercase tracking-widest text-slate-400 px-1">Onvolledige Albums</h3>
                <div class="grid grid-cols-2 gap-3">
                    <button 
                        v-for="rep in albumReports" 
                        :key="rep.key"
                        @click="router.push(`/reports/${rep.key}`)"
                        class="flex flex-col items-center bg-white dark:bg-surface-dark p-6 rounded-2xl border border-slate-100 dark:border-slate-800 hover:shadow-md transition text-center group active:scale-[0.98]"
                    >
                        <span class="material-symbols-outlined text-slate-300 mb-2 group-hover:scale-110 transition-transform">{{ rep.icon }}</span>
                        <p class="text-2xl font-black mb-1" :class="stats[rep.key] > 0 ? 'text-rose-500' : 'text-slate-300'">{{ stats[rep.key] }}</p>
                        <p class="text-[10px] font-bold uppercase text-slate-500 tracking-tight leading-tight">{{ rep.title }}</p>
                    </button>
                </div>
            </section>
        </template>

    </div>
  </div>
</template>
