<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const albumId = route.params.id

const album = ref<any>(null)
const loading = ref(true)
const error = ref('')

// Edit state
const isEditing = ref(false)
const locations = ref<any[]>([])
const allTags = ref<any[]>([])
const editForm = ref<any>({})

async function fetchAlbum() {
    loading.value = true
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/${albumId}`)
        if (response.ok) {
            const data = await response.json()
            console.log("Album loaded:", data)
            album.value = data
            
            // Init edit form safe
            editForm.value = {
                title: data.title,
                year: data.year,
                catalog_no: data.catalog_no,
                location_id: data.location?.id || null,
                tag_ids: data.tags ? data.tags.map((t:any) => t.id) : [],
                notes: data.notes
            }
        } else {
            error.value = 'Album niet gevonden'
        }
    } catch (e) {
        console.error(e)
        error.value = 'Kon album niet laden'
    } finally {
        loading.value = false
    }
}

async function fetchMetadata() {
    try {
        const [locRes, tagRes] = await Promise.all([
            fetch(`${import.meta.env.VITE_API_URL}/locations/`),
            fetch(`${import.meta.env.VITE_API_URL}/tags/`)
        ])
        if (locRes.ok) locations.value = await locRes.json()
        if (tagRes.ok) allTags.value = await tagRes.json()
    } catch(e) { console.error(e) }
}

async function saveChanges() {
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/${albumId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(editForm.value)
        })
        
        if (response.ok) {
            await fetchAlbum()
            isEditing.value = false
        } else {
            alert('Opslaan mislukt')
        }
    } catch (e) {
        alert('Opslaan mislukt')
    }
}

// Favorite Logic
const isFavorite = computed(() => {
    if (!album.value || !album.value.tags) return false
    return album.value.tags.some((t:any) => t.name === 'Favoriet')
})

async function toggleFavorite() {
    if (!album.value) return

    if (allTags.value.length === 0) {
        await fetchMetadata()
    }

    const favTag = allTags.value.find(t => t.name === 'Favoriet')
    if (!favTag) {
        alert("Tag 'Favoriet' niet gevonden. Maak deze eerst aan bij Tags.")
        return
    }

    const currentTagIds = album.value.tags.map((t:any) => t.id)
    let newTagIds = []

    if (isFavorite.value) {
        newTagIds = currentTagIds.filter((id:number) => id !== favTag.id)
    } else {
        newTagIds = [...currentTagIds, favTag.id]
    }

    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/${albumId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tag_ids: newTagIds })
        })
        if (response.ok) {
            await fetchAlbum()
        }
    } catch (e) {
        console.error(e)
    }
}

async function deleteAlbum() {
    if (!confirm('Weet je zeker dat je dit album wilt verwijderen?')) return
    
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/${albumId}`, {
            method: 'DELETE'
        })
        if (response.ok) {
            router.push('/collection')
        }
    } catch (e) {
        alert('Verwijderen mislukt')
    }
}

function startEdit() {
    fetchMetadata()
    isEditing.value = true
}

onMounted(() => {
    fetchAlbum()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-background-dark pb-20">
    
    <!-- HEADER -->
    <div class="sticky top-0 z-40 bg-gray-50/90 dark:bg-background-dark/90 backdrop-blur-md p-4 flex justify-between items-center">
        <button @click="router.back()" class="flex items-center text-primary font-bold gap-1 hover:text-blue-700 transition">
            <span class="material-symbols-outlined text-xl">arrow_back_ios_new</span>
            Terug
        </button>
        
        <div class="flex gap-2">
            <button v-if="!isEditing" @click="deleteAlbum" class="p-2 bg-red-50 dark:bg-red-900/20 rounded-lg text-red-600 dark:text-red-400 hover:bg-red-100">
                <span class="material-symbols-outlined text-xl">delete</span>
            </button>
            <button v-else @click="isEditing = false" class="text-slate-500 font-bold text-sm px-4">
                Annuleren
            </button>
        </div>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>

    <div v-else-if="error" class="p-8 text-center text-red-500 font-bold">
        {{ error }}
    </div>

    <div v-else-if="album" class="px-6 flex flex-col gap-8 max-w-lg mx-auto">
        
        <!-- COVER & TITLE -->
        <div class="flex flex-col items-center text-center relative">
            <div class="relative w-64 h-64 mb-6 rounded-2xl shadow-xl overflow-hidden bg-white">
                <img v-if="album.cover_url" :src="album.cover_url" class="w-full h-full object-cover" :alt="album.title">
                <div v-else class="w-full h-full bg-gray-200 flex items-center justify-center">
                    <span class="material-symbols-outlined text-6xl text-gray-400">album</span>
                </div>
                <!-- Shine effect -->
                <div class="absolute inset-0 bg-gradient-to-tr from-white/10 to-transparent pointer-events-none"></div>
            </div>
            
            <h1 class="text-3xl font-black text-slate-900 dark:text-white leading-tight mb-2">{{ album.title }}</h1>
            <p class="text-xl font-bold text-primary mb-4" v-if="album.artists && album.artists.length">
                {{ album.artists.map((a:any) => a.name).join(', ') }}
            </p>

            <!-- Action Bar (View Mode) -->
            <div v-if="!isEditing" class="flex gap-3 mb-4">
                <button @click="startEdit" class="flex items-center gap-2 bg-primary text-white px-5 py-2.5 rounded-full font-bold shadow-lg shadow-primary/30 hover:bg-blue-700 transition active:scale-95">
                    <span class="material-symbols-outlined text-lg">edit</span>
                    Bewerken
                </button>
                <!-- Favorite Toggle -->
                <button 
                    @click="toggleFavorite"
                    class="flex items-center gap-2 border px-4 py-2.5 rounded-full font-bold transition active:scale-95"
                    :class="isFavorite 
                        ? 'bg-rose-50 border-rose-200 text-rose-500' 
                        : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-200 border-slate-200 dark:border-slate-700 hover:bg-slate-50'"
                >
                    <span class="material-symbols-outlined text-lg" :class="{ 'icon-filled': isFavorite }">favorite</span>
                </button>
            </div>

            <!-- Tags -->
            <div class="flex flex-wrap justify-center gap-2">
                <span 
                    v-for="tag in album.tags" :key="tag.id"
                    class="px-3 py-1 rounded-full text-xs font-bold shadow-sm text-white"
                    :style="{ backgroundColor: tag.color }"
                >
                    {{ tag.name }}
                </span>
            </div>
        </div>

        <!-- INFO GRID (View Mode) -->
        <div v-if="!isEditing" class="bg-white dark:bg-surface-dark rounded-2xl p-6 shadow-sm border border-slate-100 dark:border-slate-800 grid grid-cols-2 gap-y-6 gap-x-4">
            
            <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-[18px]">calendar_today</span>
                    <span class="text-xs font-bold uppercase">Jaar</span>
                </div>
                <p class="font-bold text-slate-900 dark:text-white">{{ album.year }}</p>
            </div>

            <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-[18px]">music_note</span>
                    <span class="text-xs font-bold uppercase">Genre</span>
                </div>
                <p class="font-bold text-slate-900 dark:text-white">Rock (Placeholder)</p>
            </div>

            <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-[18px]">barcode</span>
                    <span class="text-xs font-bold uppercase">Catalogus #</span>
                </div>
                <p class="font-bold text-slate-900 dark:text-white">{{ album.catalog_no || '-' }}</p>
            </div>

            <div class="col-span-2 flex flex-col gap-1">
                <div class="flex items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-[18px]">shelves</span>
                    <span class="text-xs font-bold uppercase">Locatie</span>
                </div>
                <div class="flex items-center justify-between">
                    <div>
                        <p class="font-bold text-slate-900 dark:text-white text-lg">
                            {{ album.location ? `${album.location.name} (${album.location.storage_type})` : 'Nog niet ingedeeld' }}
                        </p>
                        <p v-if="album.location?.shelf" class="text-sm text-slate-500">
                            {{ album.location.shelf }}
                        </p>
                    </div>
                    <span v-if="!album.location" class="text-xs text-red-500 font-bold bg-red-50 px-2 py-1 rounded">Missend</span>
                </div>
            </div>

        </div>

        <!-- EDIT MODE FORM -->
        <div v-else class="flex flex-col gap-4 animate-in fade-in bg-white dark:bg-surface-dark p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
            <h3 class="font-bold text-lg mb-2 dark:text-white">Album Bewerken</h3>
            
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Titel</label>
                <input v-model="editForm.title" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-bold text-slate-900 dark:text-white focus:ring-primary">
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Jaar</label>
                    <input v-model="editForm.year" type="number" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Catalogus Nr.</label>
                    <input v-model="editForm.catalog_no" type="text" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary">
                </div>
            </div>
            
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Locatie</label>
                <select v-model="editForm.location_id" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary">
                    <option :value="null">Geen</option>
                    <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
                </select>
            </div>

            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Tags</label>
                <div class="flex flex-wrap gap-2">
                    <button 
                        v-for="tag in allTags" :key="tag.id"
                        @click="editForm.tag_ids.includes(tag.id) ? editForm.tag_ids = editForm.tag_ids.filter((id:any) => id !== tag.id) : editForm.tag_ids.push(tag.id)"
                        class="px-3 py-1 rounded-full text-xs font-bold border transition-all"
                        :class="editForm.tag_ids.includes(tag.id) ? 'bg-primary text-white border-primary' : 'bg-slate-50 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-600'"
                        :style="editForm.tag_ids.includes(tag.id) ? { backgroundColor: tag.color, borderColor: tag.color } : {}"
                    >
                        {{ tag.name }}
                    </button>
                </div>
            </div>
            
            <div>
                 <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Notities</label>
                 <textarea v-model="editForm.notes" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 text-slate-700 dark:text-white focus:ring-primary" rows="3"></textarea>
            </div>

            <div class="flex gap-3 pt-2">
                <button @click="isEditing = false" class="flex-1 py-3 text-slate-500 font-bold hover:bg-slate-100 rounded-xl">Annuleren</button>
                <button @click="saveChanges" class="flex-1 py-3 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/30">Opslaan</button>
            </div>
        </div>

        <!-- TRACKLIST -->
        <div v-if="!isEditing">
            <h3 class="font-bold text-slate-900 dark:text-white text-sm uppercase tracking-wide mb-3">Tracklist</h3>
            <div class="bg-white dark:bg-surface-dark rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 divide-y divide-slate-100 dark:divide-slate-800">
                
                <!-- Placeholder Tracks -->
                <div class="p-4 flex items-center gap-4 text-slate-400 italic text-sm justify-center">
                    <span class="material-symbols-outlined">playlist_play</span>
                    <span>Tracklist data volgt in update</span>
                </div>
            </div>
        </div>

        <!-- NOTES -->
        <div v-if="album.notes && !isEditing">
            <h3 class="font-bold text-slate-900 dark:text-white text-sm uppercase tracking-wide mb-3">Notes</h3>
            <div class="bg-amber-50 dark:bg-amber-900/10 border border-amber-100 dark:border-amber-900/20 p-4 rounded-xl flex gap-3">
                <span class="material-symbols-outlined text-amber-600 dark:text-amber-500">sticky_note_2</span>
                <p class="text-sm text-slate-700 dark:text-slate-300 font-medium leading-relaxed">{{ album.notes }}</p>
            </div>
        </div>

    </div>
  </div>
</template>