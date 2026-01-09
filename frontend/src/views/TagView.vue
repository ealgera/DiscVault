<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Tag {
  id: number
  name: string
  color: string
  album_count?: number
}

const tags = ref<Tag[]>([])
const loading = ref(true)
const error = ref('')

// Form state
const showAddForm = ref(false)
const editingTagId = ref<number | null>(null)
const newTag = ref({
    name: '',
    color: '#135bec' // Default to primary blue
})

// Predefined colors for quick picking
const colors = [
    '#135bec', '#10b981', '#f59e0b', '#ef4444', 
    '#8b5cf6', '#ec4899', '#64748b', '#334155'
]

async function fetchTags() {
    loading.value = true
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/tags/`)
        if (response.ok) {
            tags.value = await response.json()
        }
    } catch (e) {
        error.value = 'Kon tags niet laden.'
    } finally {
        loading.value = false
    }
}

function startEdit(tag: Tag) {
    newTag.value = { ...tag }
    editingTagId.value = tag.id
    showAddForm.value = true
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

function resetForm() {
    newTag.value = { name: '', color: '#135bec' }
    editingTagId.value = null
    showAddForm.value = false
}

async function saveTag() {
    if (!newTag.value.name) return

    try {
        let url = `${import.meta.env.VITE_API_URL}/tags/`
        let method = 'POST'

        if (editingTagId.value) {
            url += `${editingTagId.value}`
            method = 'PUT'
        }

        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newTag.value)
        })
        
        if (response.ok) {
            await fetchTags()
            resetForm()
        }
    } catch (e) {
        alert('Fout bij opslaan tag')
    }
}

onMounted(() => {
    fetchTags()
})
</script>

<template>
  <div class="p-4 max-w-md mx-auto pb-24">

    <!-- Sub Nav -->
    <div class="flex gap-4 mb-6 border-b border-slate-200 dark:border-slate-800">
        <router-link to="/locations" class="pb-2 text-sm font-medium text-slate-400 hover:text-slate-600">Locaties</router-link>
        <router-link to="/tags" class="pb-2 text-sm font-bold border-b-2 border-primary text-primary">Tags</router-link>
        <router-link to="/genres" class="pb-2 text-sm font-medium text-slate-400 hover:text-slate-600">Genres</router-link>
    </div>

    <div class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Tags</h1>
        <button @click="showAddForm ? resetForm() : (showAddForm = true)" class="bg-primary text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm">
            {{ showAddForm ? 'Annuleren' : '+ Nieuw' }}
        </button>
    </div>

    <!-- ADD/EDIT FORM -->
    <div v-if="showAddForm" class="bg-white dark:bg-surface-dark p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 mb-6 animate-in slide-in-from-top-2">
        <h2 class="font-bold mb-4 dark:text-white">{{ editingTagId ? 'Wijzig Tag' : 'Nieuwe Tag' }}</h2>
        <form @submit.prevent="saveTag" class="flex flex-col gap-4">
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Naam</label>
                <input v-model="newTag.name" type="text" class="w-full rounded-lg border-slate-300 dark:bg-slate-800 dark:border-slate-600 dark:text-white" required placeholder="bijv. Favoriet">
            </div>
            
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Kleur</label>
                <div class="flex flex-wrap gap-2 mb-2">
                    <button 
                        v-for="c in colors" :key="c"
                        type="button"
                        @click="newTag.color = c"
                        class="size-8 rounded-full border-2 transition-transform active:scale-90"
                        :class="newTag.color === c ? 'border-slate-900 dark:border-white scale-110' : 'border-transparent'"
                        :style="{ backgroundColor: c }"
                    ></button>
                    <!-- Custom color input -->
                    <input type="color" v-model="newTag.color" class="size-8 rounded-full border-none p-0 cursor-pointer overflow-hidden">
                </div>
            </div>

            <!-- Preview Badge -->
            <div class="flex items-center gap-2 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                <span class="text-sm font-medium">Preview:</span>
                <span 
                    class="px-3 py-1 rounded-full text-white text-xs font-bold"
                    :style="{ backgroundColor: newTag.color }"
                >
                    {{ newTag.name || 'Label' }}
                </span>
            </div>

            <button type="submit" class="bg-primary text-white py-3 rounded-lg font-bold mt-2">{{ editingTagId ? 'Opslaan' : 'Toevoegen' }}</button>
        </form>
    </div>

    <!-- LIST -->
    <div v-if="loading" class="text-center py-8">Laden...</div>
    <div v-else class="flex flex-col gap-3">
        <div v-for="tag in tags" :key="tag.id" @click="startEdit(tag)" class="bg-white dark:bg-surface-dark p-4 rounded-xl border border-slate-100 dark:border-slate-800 flex items-center justify-between cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition">
            <div class="flex items-center gap-3">
                <div class="size-4 rounded-full" :style="{ backgroundColor: tag.color }"></div>
                <h3 class="font-bold text-slate-900 dark:text-white">
                    {{ tag.name }}
                    <span class="text-xs text-slate-400 font-normal ml-2">({{ tag.album_count || 0 }})</span>
                </h3>
            </div>
            <span 
                class="px-2 py-0.5 rounded-full text-white text-[10px] font-bold"
                :style="{ backgroundColor: tag.color }"
            >
                LABEL
            </span>
        </div>

        <div v-if="tags.length === 0" class="text-center text-slate-400 py-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-dashed border-slate-300 dark:border-slate-700">
            Nog geen tags. Maak er eentje aan!
        </div>
    </div>

  </div>
</template>
