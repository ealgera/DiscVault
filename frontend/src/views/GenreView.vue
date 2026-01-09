<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Genre {
  id: number
  name: string
  album_count?: number
}

const genres = ref<Genre[]>([])
const loading = ref(true)
const error = ref('')

// Form state
const showAddForm = ref(false)
const editingGenreId = ref<number | null>(null)
const newGenre = ref({
    name: ''
})

async function fetchGenres() {
    loading.value = true
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/genres/`)
        if (response.ok) {
            genres.value = await response.json()
        }
    } catch (e) {
        error.value = 'Kon genres niet laden.'
    } finally {
        loading.value = false
    }
}

function startEdit(genre: Genre) {
    newGenre.value = { ...genre }
    editingGenreId.value = genre.id
    showAddForm.value = true
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

function resetForm() {
    newGenre.value = { name: '' }
    editingGenreId.value = null
    showAddForm.value = false
}

async function saveGenre() {
    if (!newGenre.value.name) return

    try {
        let url = `${import.meta.env.VITE_API_URL}/genres/`
        let method = 'POST'

        if (editingGenreId.value) {
            url += `${editingGenreId.value}`
            method = 'PUT'
        }

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newGenre.value)
        })
        
        if (response.ok) {
            await fetchGenres()
            resetForm()
        }
    } catch (e) {
        alert('Fout bij opslaan genre')
    }
}

async function deleteGenre(id: number, name: string) {
    if (!confirm(`Weet je zeker dat je "${name}" wilt verwijderen? Het wordt losgekoppeld van alle albums.`)) return

    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/genres/${id}`, {
            method: 'DELETE'
        })
        if (response.ok) {
            await fetchGenres()
        }
    } catch (e) {
        alert('Kon genre niet verwijderen')
    }
}

onMounted(() => {
    fetchGenres()
})
</script>

<template>
  <div class="p-4 max-w-md mx-auto pb-24">

    <!-- Sub Nav -->
    <div class="flex gap-4 mb-6 border-b border-slate-200 dark:border-slate-800">
        <router-link to="/locations" class="pb-2 text-sm font-medium text-slate-400 hover:text-slate-600">Locaties</router-link>
        <router-link to="/tags" class="pb-2 text-sm font-medium text-slate-400 hover:text-slate-600">Tags</router-link>
        <router-link to="/genres" class="pb-2 text-sm font-bold border-b-2 border-primary text-primary">Genres</router-link>
    </div>

    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Genres</h1>
        <button @click="showAddForm ? resetForm() : (showAddForm = true)" class="bg-primary text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm">
            {{ showAddForm ? 'Annuleren' : '+ Nieuw' }}
        </button>
    </div>

    <!-- ADD/EDIT FORM -->
    <div v-if="showAddForm" class="bg-white dark:bg-surface-dark p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 mb-6 animate-in slide-in-from-top-2">
        <h2 class="font-bold mb-4 dark:text-white">{{ editingGenreId ? 'Wijzig Genre' : 'Nieuw Genre' }}</h2>
        <form @submit.prevent="saveGenre" class="flex flex-col gap-4">
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Naam</label>
                <input v-model="newGenre.name" type="text" class="w-full rounded-lg border-slate-300 dark:bg-slate-800 dark:border-slate-600 dark:text-white" required placeholder="bijv. Jazz">
            </div>
            
            <button type="submit" class="bg-primary text-white py-3 rounded-lg font-bold mt-2">{{ editingGenreId ? 'Opslaan' : 'Toevoegen' }}</button>
        </form>
    </div>

    <!-- LIST -->
    <div v-if="loading" class="text-center py-8">Laden...</div>
    <div v-else class="flex flex-col gap-3">
        <div v-for="genre in genres" :key="genre.id" class="bg-white dark:bg-surface-dark p-4 rounded-xl border border-slate-100 dark:border-slate-800 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-800 transition">
            <h3 @click="startEdit(genre)" class="font-bold text-slate-900 dark:text-white flex-1 cursor-pointer">
                {{ genre.name }} 
                <span class="text-xs text-slate-400 font-normal ml-2">({{ genre.album_count || 0 }})</span>
            </h3>
            <div class="flex gap-2">
                <button @click="startEdit(genre)" class="text-slate-300 hover:text-primary p-2">
                    <span class="material-symbols-outlined">edit</span>
                </button>
                <button @click="deleteGenre(genre.id, genre.name)" class="text-slate-300 hover:text-red-500 p-2">
                    <span class="material-symbols-outlined">delete</span>
                </button>
            </div>
        </div>

        <div v-if="genres.length === 0" class="text-center text-slate-400 py-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
            Nog geen genres. Deze worden automatisch toegevoegd bij het scannen!
        </div>
    </div>

  </div>
</template>
