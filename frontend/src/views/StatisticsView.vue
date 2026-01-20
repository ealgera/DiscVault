<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const genreDistribution = ref<any[]>([])
const tagDistribution = ref<any[]>([])
const loading = ref(true)
const error = ref('')

async function fetchStatistics() {
    loading.value = true
    try {
        const [genRes, tagRes] = await Promise.all([
            fetch(`${import.meta.env.VITE_API_URL}/reports/distribution/genres`),
            fetch(`${import.meta.env.VITE_API_URL}/reports/distribution/tags`)
        ])
        
        if (genRes.ok) genreDistribution.value = await genRes.json()
        if (tagRes.ok) tagDistribution.value = await tagRes.json()
        
    } catch (e) {
        error.value = 'Fout bij ophalen statistieken'
    } finally {
        loading.value = false
    }
}

onMounted(fetchStatistics)

function getPercentage(count: number, total: number) {
    if (total === 0) return 0
    return Math.round((count / total) * 100)
}

const totalGenreCount = ref(0)
const totalTagCount = ref(0)

onMounted(async () => {
    // We already fetch, but let's compute totals for progress bars
    // Note: the backend 'limit 10' means these totals are only for the top 10.
    // To be accurate, we'd need another endpoint or the backend to provide the grand total.
    // For now, let's just use the max value for scaling.
})

const maxGenreCount = ref(0)
const maxTagCount = ref(0)

onMounted(async () => {
    await fetchStatistics()
    if (genreDistribution.value.length > 0) {
        maxGenreCount.value = Math.max(...genreDistribution.value.map(i => i.count))
    }
    if (tagDistribution.value.length > 0) {
        maxTagCount.value = Math.max(...tagDistribution.value.map(i => i.count))
    }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-background-dark pb-20">
    <!-- Header -->
    <div class="sticky top-0 z-40 bg-gray-50/90 dark:bg-background-dark/90 backdrop-blur-md p-4 flex items-center gap-4">
        <button @click="router.back()" class="flex items-center text-primary font-bold gap-1 hover:text-blue-700 transition">
            <span class="material-symbols-outlined text-xl">arrow_back_ios_new</span>
            Terug
        </button>
        <h1 class="text-xl font-black text-slate-900 dark:text-white">Statistieken</h1>
    </div>

    <div class="p-6 max-w-lg mx-auto space-y-8">
        <div v-if="loading" class="flex justify-center py-20">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
        
        <template v-else>
            <!-- Genres Chart -->
            <section class="bg-white dark:bg-surface-dark p-6 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm">
                <div class="flex items-center gap-3 mb-6">
                    <div class="size-10 rounded-2xl bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center">
                        <span class="material-symbols-outlined text-blue-500">category</span>
                    </div>
                    <div>
                        <h2 class="font-black text-slate-900 dark:text-white uppercase tracking-tight">Top 10 Genres</h2>
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">In je collectie</p>
                    </div>
                </div>

                <div class="space-y-4">
                    <div v-for="item in genreDistribution" :key="item.name" class="space-y-1">
                        <div class="flex justify-between text-xs font-bold">
                            <span class="text-slate-700 dark:text-slate-300">{{ item.name }}</span>
                            <span class="text-slate-400">{{ item.count }}</span>
                        </div>
                        <div class="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div 
                                class="h-full bg-blue-500 rounded-full transition-all duration-1000"
                                :style="{ width: `${(item.count / maxGenreCount) * 100}%` }"
                            ></div>
                        </div>
                    </div>
                    <div v-if="genreDistribution.length === 0" class="text-center py-4 text-slate-400 text-xs italic">
                        Geen gegevens beschikbaar
                    </div>
                </div>
            </section>

            <!-- Tags Chart -->
            <section class="bg-white dark:bg-surface-dark p-6 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm">
                <div class="flex items-center gap-3 mb-6">
                    <div class="size-10 rounded-2xl bg-purple-50 dark:bg-purple-900/20 flex items-center justify-center">
                        <span class="material-symbols-outlined text-purple-500">tag</span>
                    </div>
                    <div>
                        <h2 class="font-black text-slate-900 dark:text-white uppercase tracking-tight">Top 10 Tags</h2>
                        <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">In je collectie</p>
                    </div>
                </div>

                <div class="space-y-4">
                    <div v-for="item in tagDistribution" :key="item.name" class="space-y-1">
                        <div class="flex justify-between text-xs font-bold">
                            <span class="text-slate-700 dark:text-slate-300">{{ item.name }}</span>
                            <span class="text-slate-400">{{ item.count }}</span>
                        </div>
                        <div class="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div 
                                class="h-full bg-purple-500 rounded-full transition-all duration-1000"
                                :style="{ width: `${(item.count / maxTagCount) * 100}%` }"
                            ></div>
                        </div>
                    </div>
                    <div v-if="tagDistribution.length === 0" class="text-center py-4 text-slate-400 text-xs italic">
                        Geen gegevens beschikbaar
                    </div>
                </div>
            </section>
        </template>
    </div>
  </div>
</template>
