<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const reportType = route.params.type as string

const items = ref<any[]>([])
const loading = ref(true)
const error = ref('')

const isMetadataReport = computed(() => 
    ['unused_genres', 'low_usage_genres', 'unused_tags', 'low_usage_tags', 'unused_artists'].includes(reportType)
)

const reportTitle = computed(() => {
    const titles: any = {
        unused_genres: 'Ongebruikte Genres',
        low_usage_genres: 'Weinig gebruikte Genres',
        unused_tags: 'Ongebruikte Tags',
        low_usage_tags: 'Weinig gebruikte Tags',
        unused_artists: 'Artiesten zonder album',
        missing_covers: 'Zonder Hoes',
        missing_tracks: 'Zonder Tracks',
        missing_year: 'Zonder Jaar',
        missing_location: 'Zonder Locatie',
        missing_media: 'Zonder Media type',
        missing_catalog: 'Zonder Catalogus #',
    }
    return titles[reportType] || 'Rapport Detail'
})

async function fetchDetails() {
    loading.value = true
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/reports/details/${reportType}`)
        if (response.ok) {
            items.value = await response.json()
        } else {
            error.value = 'Kon details niet laden'
        }
    } catch (e) {
        error.value = 'Fout bij verbinden met server'
    } finally {
        loading.value = false
    }
}

async function deleteMetadata(id: number) {
    let endpoint = ''
    if (reportType.includes('genre')) endpoint = 'genres'
    else if (reportType.includes('tag')) endpoint = 'tags'
    else if (reportType.includes('artist')) endpoint = 'artists'

    if (!endpoint) return
    if (!confirm('Weet je zeker dat je dit item wilt verwijderen?')) return

    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/${endpoint}/${id}`, {
            method: 'DELETE'
        })
        if (response.ok) {
            items.value = items.value.filter(i => i.id !== id)
        } else {
            alert('Verwijderen mislukt (mogelijk nog in gebruik)')
        }
    } catch (e) {
        alert('Fout bij verwijderen')
    }
}

function searchMetadata(name: string) {
    let filter = 'all'
    if (reportType.includes('genre')) filter = 'genre'
    else if (reportType.includes('tag')) filter = 'tag'
    else if (reportType.includes('artist')) filter = 'artist'
    
    router.push({
        path: '/collection',
        query: { q: name, filter: filter }
    })
}

onMounted(fetchDetails)
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-background-dark pb-20">
    <div class="sticky top-0 z-40 bg-gray-50/90 dark:bg-background-dark/90 backdrop-blur-md p-4 flex items-center justify-between">
        <button @click="router.back()" class="flex items-center text-primary font-bold gap-1 hover:text-blue-700 transition">
            <span class="material-symbols-outlined text-xl">arrow_back_ios_new</span>
            Terug
        </button>
        <h1 class="text-sm font-black text-slate-400 uppercase tracking-widest">{{ reportTitle }}</h1>
        <div class="w-10"></div> <!-- Spacer -->
    </div>

    <div class="p-6 max-w-lg mx-auto">
        
        <div v-if="loading" class="flex justify-center py-20">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        <div v-else-if="error" class="bg-red-50 text-red-600 p-4 rounded-xl font-bold text-center">
            {{ error }}
        </div>

        <div v-else>
            <div v-if="items.length === 0" class="text-center py-20 text-slate-400 space-y-4">
                <span class="material-symbols-outlined text-6xl opacity-20">check_circle</span>
                <p class="font-bold">Alles ziet er goed uit!</p>
            </div>

            <div v-else class="space-y-3">
                <!-- METADATA LIST -->
                <template v-if="isMetadataReport">
                    <div 
                        v-for="item in items" :key="item.id"
                        class="bg-white dark:bg-surface-dark p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex items-center justify-between"
                    >
                        <div class="flex flex-col">
                            <div class="flex items-center gap-2">
                                <span class="font-bold text-slate-800 dark:text-white">{{ item.name }}</span>
                                <span v-if="item.count !== undefined" class="text-xs font-medium text-slate-400">({{ item.count }})</span>
                            </div>
                            <span class="text-[10px] uppercase font-bold text-slate-400">ID: {{ item.id }}</span>
                        </div>
                        <div class="flex items-center gap-2">
                            <button @click="searchMetadata(item.name)" class="size-10 flex items-center justify-center rounded-full bg-blue-50 dark:bg-blue-900/20 text-primary hover:bg-blue-100 transition">
                                <span class="material-symbols-outlined">search</span>
                            </button>
                            <button @click="deleteMetadata(item.id)" class="size-10 flex items-center justify-center rounded-full bg-red-50 dark:bg-red-900/20 text-red-500 hover:bg-red-100 transition">
                                <span class="material-symbols-outlined">delete</span>
                            </button>
                        </div>
                    </div>
                </template>

                <!-- ALBUM LIST -->
                <template v-else>
                    <div 
                        v-for="album in items" :key="album.id"
                        @click="router.push(`/albums/${album.id}`)"
                        class="bg-white dark:bg-surface-dark p-4 rounded-2xl border border-slate-100 dark:border-slate-800 flex items-center gap-4 hover:shadow-md transition cursor-pointer active:scale-[0.98]"
                    >
                        <div class="size-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0">
                            <span class="material-symbols-outlined text-slate-300">album</span>
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="font-bold text-slate-800 dark:text-white truncate">{{ album.title }}</p>
                            <p class="text-xs text-slate-500 truncate" v-if="album.artists">
                                {{ album.artists.map((a:any) => a.name).join(', ') }}
                            </p>
                        </div>
                        <span class="material-symbols-outlined text-slate-300">chevron_right</span>
                    </div>
                </template>
            </div>
        </div>

    </div>
  </div>
</template>
