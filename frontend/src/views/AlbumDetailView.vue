<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const albumId = route.params.id

interface Album {
  id: number
  title: string
  year: number
  artists: { id: number, name: string }[]
  cover_url?: string
  location?: { id: number, name: string, storage_type: string, shelf?: string }
  tags?: { id: number, name: string, color: string }[]
  genres?: { id: number, name: string }[]
  catalog_no?: string
  upc_ean?: string
  notes?: string
  media_type: string
  spars_code?: string
  created_at: string
  tracks?: { track_no: number, title: string, duration: string, disc_no: number, disc_name?: string }[]
}

const album = ref<Album | null>(null)
const loading = ref(true)
const error = ref('')

// Edit state
const isEditing = ref(false)
const locations = ref<any[]>([])
const allTags = ref<any[]>([])
const allGenres = ref<any[]>([])
const editForm = ref<any>({})
const artistInput = ref('')
const selectedFile = ref<File | null>(null)
const coverPreview = ref<string | null>(null)

const mediaTypes = ref<string[]>([])

// Bulk Import
const showBulkModal = ref(false)
const bulkText = ref('')
const parsedPreview = ref<any[]>([])
const isParsing = ref(false)
const bulkError = ref('')

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
                upc_ean: data.upc_ean,
                location_id: data.location?.id || null,
                tag_ids: data.tags ? data.tags.map((t:any) => t.id) : [],
                genre_ids: data.genres ? data.genres.map((g:any) => g.id) : [],
                artist_names: data.artists ? data.artists.map((a:any) => a.name) : [],
                notes: data.notes,
                media_type: data.media_type || 'CD',
                spars_code: data.spars_code || '',
                cover_url: data.cover_url,
                tracks: data.tracks || []
            }
            artistInput.value = editForm.value.artist_names.join(', ')
        }
 else {
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
        const results = await Promise.allSettled([
            fetch(`${import.meta.env.VITE_API_URL}/locations/`),
            fetch(`${import.meta.env.VITE_API_URL}/tags/`),
            fetch(`${import.meta.env.VITE_API_URL}/genres/`),
            fetch(`${import.meta.env.VITE_API_URL}/constants`)
        ])
        
        if (results[0].status === 'fulfilled' && results[0].value.ok) locations.value = await results[0].value.json()
        if (results[1].status === 'fulfilled' && results[1].value.ok) allTags.value = await results[1].value.json()
        if (results[2].status === 'fulfilled' && results[2].value.ok) allGenres.value = await results[2].value.json()
        if (results[3].status === 'fulfilled' && results[3].value.ok) {
            const data = await results[3].value.json()
            mediaTypes.value = data.media_types
        }
        
    } catch(e) { console.error("Metadata fetch error:", e) }
}

function onCoverChange(e: any) {
    const file = e.target.files[0]
    if (file) {
        selectedFile.value = file
        coverPreview.value = URL.createObjectURL(file)
    }
}

async function saveChanges() {
    try {
        // 1. Handle Cover Upload if exists
        if (selectedFile.value) {
            const formData = new FormData()
            formData.append('file', selectedFile.value)
            const uploadRes = await fetch(`${import.meta.env.VITE_API_URL}/albums/${albumId}/cover`, {
                method: 'POST',
                body: formData
            })
            if (uploadRes.ok) {
                const uploadData = await uploadRes.json()
                editForm.value.cover_url = uploadData.cover_url
            }
        }

        // 2. Save rest of metadata
        const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/${albumId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(editForm.value)
        })
        
        if (response.ok) {
            await fetchAlbum()
            isEditing.value = false
            selectedFile.value = null
            coverPreview.value = null
        } else {
            alert('Opslaan mislukt')
        }
    } catch (e) {
        alert('Opslaan mislukt')
    } finally {
        loading.value = false
    }
}

// Favorite Logic
const isFavorite = computed(() => {
    const currentAlbum = album.value
    if (!currentAlbum) return false
    
    // Explicitly check for tags existence
    if (!currentAlbum.tags) return false
    
    // Use optional chaining just in case, though the above check should cover it
    return currentAlbum.tags.some((t:any) => t.name === 'Favoriet')
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

    const currentTagIds = album.value.tags ? album.value.tags.map((t:any) => t.id) : []
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

async function syncWithMusicBrainz() {
    if (!album.value?.upc_ean) return
    
    loading.value = true
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/${albumId}/sync`, {
            method: 'POST'
        })
        if (response.ok) {
            await fetchAlbum()
        } else {
            const data = await response.json()
            alert(data.detail || 'Sync mislukt')
        }
    } catch (e) {
        alert('Fout bij synchroniseren')
    } finally {
        loading.value = false
    }
}

function startEdit() {
    fetchMetadata()
    isEditing.value = true
}

function resolveCoverURL(url: string | undefined) {
    if (!url) return undefined
    if (url.startsWith('http')) return url
    const baseUrl = import.meta.env.VITE_API_URL.replace(/\/$/, '')
    const path = url.startsWith('/') ? url : `/${url}`
    return `${baseUrl}${path}`
}


async function handleBulkParse(e?: Event) {
    const file = e ? (e.target as HTMLInputElement).files?.[0] : null
    isParsing.value = true
    bulkError.value = ""
    
    try {
        let response
        const formData = new FormData()
        
        if (file) {
            formData.append('file', file)
        } else {
            formData.append('text', bulkText.value)
        }

        response = await fetch(`${import.meta.env.VITE_API_URL}/tracks/parse`, {
            method: 'POST',
            body: formData
        })
        
        if (response.ok) {
            parsedPreview.value = await response.json()
        } else {
            const detail = await response.json()
            bulkError.value = detail.detail || "Parsen mislukt"
        }
    } catch (e) {
        bulkError.value = "Fout bij verbinden met server"
    } finally {
        isParsing.value = false
    }
}

function confirmBulkImport() {
    if (!editForm.value) return
    editForm.value.tracks = parsedPreview.value.map((t: any) => ({
        ...t,
        track_no: t.position
    }))
    showBulkModal.value = false
    bulkText.value = ""
    parsedPreview.value = []
}

function addTrack() {
    if (!editForm.value.tracks) editForm.value.tracks = []
    const lastTrack = editForm.value.tracks[editForm.value.tracks.length - 1]
    const nextDisc = lastTrack ? lastTrack.disc_no : 1
    const nextNo = lastTrack ? lastTrack.track_no + 1 : 1
    
    editForm.value.tracks.push({
        track_no: nextNo,
        title: '',
        duration: '',
        disc_no: nextDisc,
        disc_name: lastTrack ? lastTrack.disc_name : 'Format'
    })
}

function removeTrack(index: number) {
    editForm.value.tracks.splice(index, 1)
}

const viewTracksByDisc = computed(() => {
    if (!album.value?.tracks) return {}
    return album.value.tracks.reduce((acc: any, track: any) => {
        const d = track.disc_no || 1
        if (!acc[d]) acc[d] = []
        acc[d].push(track)
        return acc
    }, {})
})

const editTracksByDisc = computed(() => {
    if (!editForm.value?.tracks) return {}
    return editForm.value.tracks.reduce((acc: any, track: any, index: number) => {
        const d = track.disc_no || 1
        if (!acc[d]) acc[d] = []
        track._originalIndex = index
        acc[d].push(track)
        return acc
    }, {})
})

const youtubeMusicUrl = computed(() => {
  if (!album.value) return '#'
  const artist = album.value.artists?.[0]?.name || ''
  const query = `${artist} ${album.value.title}`.trim()
  return `https://music.youtube.com/search?q=${encodeURIComponent(query)}`
})

function getLyricsUrl(trackTitle: string) {
  if (!album.value) return '#'
  const artist = album.value.artists?.[0]?.name || ''
  const query = `${artist} ${trackTitle} lyrics`.trim()
  return `https://www.google.com/search?q=${encodeURIComponent(query)}`
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
                <img v-if="album.cover_url" :src="resolveCoverURL(album.cover_url)" class="w-full h-full object-cover" :alt="album.title">
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
                
                <!-- YouTube Music Toggle -->
                <a 
                    :href="youtubeMusicUrl" 
                    target="_blank"
                    class="flex items-center gap-2 bg-[#FF0000] text-white px-5 py-2.5 rounded-full font-bold shadow-lg shadow-red-500/30 hover:bg-red-700 transition active:scale-95"
                >
                    <span class="material-symbols-outlined text-lg">play_circle</span>
                    YouTube Music
                </a>
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
                    <span class="material-symbols-outlined text-[18px]">album</span>
                    <span class="text-xs font-bold uppercase">Media</span>
                </div>
                <p class="font-bold text-slate-900 dark:text-white">
                    {{ album.media_type }} <span v-if="album.spars_code" class="text-xs text-slate-500 ml-1">({{ album.spars_code }})</span>
                </p>
            </div>

            <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-[18px]">music_note</span>
                    <span class="text-xs font-bold uppercase">Genre</span>
                </div>
                <p class="font-bold text-slate-900 dark:text-white line-clamp-1">
                    {{ album.genres && album.genres.length ? album.genres.map((g:any) => g.name).join(', ') : '-' }}
                </p>
            </div>

            <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-[18px]">barcode</span>
                    <span class="text-xs font-bold uppercase">Barcode (UPC/EAN)</span>
                </div>
                <div class="flex items-center gap-2">
                    <p class="font-bold text-slate-900 dark:text-white">{{ album.upc_ean || '-' }}</p>
                    <button 
                        v-if="album.upc_ean && (!album.tracks || album.tracks.length === 0)" 
                        @click="syncWithMusicBrainz"
                        class="px-2 py-1 bg-primary/10 text-primary text-[10px] font-bold rounded hover:bg-primary/20 transition flex items-center gap-1"
                    >
                        <span class="material-symbols-outlined text-xs">sync</span>
                        INFO OPHALEN
                    </button>
                </div>
            </div>

            <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-[18px]">tag</span>
                    <span class="text-xs font-bold uppercase">Catalogus #</span>
                </div>
                <p class="font-bold text-slate-900 dark:text-white">{{ album.catalog_no || '-' }}</p>
            </div>

            <div class="flex flex-col gap-1">
                <div class="flex items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-[18px]">calendar_today</span>
                    <span class="text-xs font-bold uppercase">Toegevoegd</span>
                </div>
                <p class="font-bold text-slate-900 dark:text-white text-sm">
                    {{ new Date(album.created_at).toLocaleDateString() }}
                </p>
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
            
            <!-- Cover Upload -->
            <div class="mb-2">
                <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Cover Art wijzigen</label>
                <div class="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-dashed border-slate-200 dark:border-slate-700">
                    <input type="file" @change="onCoverChange" accept="image/*" class="text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20">
                </div>
            </div>

            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Titel</label>
                <input v-model="editForm.title" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-bold text-slate-900 dark:text-white focus:ring-primary">
            </div>

            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Artist(s) <span class="text-[10px] lowercase font-normal">(komma gescheiden)</span></label>
                <input v-model="artistInput" @input="editForm.artist_names = artistInput.split(',').map(s => s.trim())" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-bold text-primary focus:ring-primary">
            </div>

            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Jaar</label>
                    <input v-model.number="editForm.year" type="number" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Media Type</label>
                    <select v-model="editForm.media_type" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary">
                        <option v-for="t in mediaTypes" :key="t" :value="t">{{ t }}</option>
                    </select>
                </div>
            </div>

            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">SPARS Code</label>
                <input v-model="editForm.spars_code" type="text" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary" placeholder="bijv. DDD">
            </div>
            
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Catalogus Nr.</label>
                    <input v-model="editForm.catalog_no" type="text" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Barcode (UPC/EAN)</label>
                    <input v-model="editForm.upc_ean" type="text" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary">
                </div>
            </div>
            
            <div>
                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Locatie</label>
                <select v-model="editForm.location_id" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 font-medium text-slate-900 dark:text-white focus:ring-primary">
                    <option :value="null">Geen</option>
                    <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.name }} ({{ loc.storage_type }})</option>
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
                <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Genres</label>
                <div class="flex flex-wrap gap-2">
                    <button 
                        v-for="genre in allGenres" :key="genre.id"
                        @click="editForm.genre_ids.includes(genre.id) ? editForm.genre_ids = editForm.genre_ids.filter((id:any) => id !== genre.id) : editForm.genre_ids.push(genre.id)"
                        class="px-3 py-1 rounded-full text-xs font-bold border transition-all"
                        :class="editForm.genre_ids.includes(genre.id) ? 'bg-primary text-white border-primary' : 'bg-slate-50 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-600'"
                    >
                        {{ genre.name }}
                    </button>
                </div>
            </div>
            
            <div>
                 <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Notities</label>
                 <textarea v-model="editForm.notes" class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-3 text-slate-700 dark:text-white focus:ring-primary" rows="3"></textarea>
            </div>

            <!-- Tracklist Management -->
            <div class="mt-4">
                <div class="flex items-center justify-between mb-2">
                    <label class="block text-xs font-bold text-slate-500 uppercase">Tracklist</label>
                    <div class="flex gap-3">
                        <button @click="showBulkModal = true" class="text-xs font-bold text-slate-500 flex items-center gap-1 hover:text-primary transition-colors">
                            <span class="material-symbols-outlined text-sm">format_list_bulleted_add</span>
                            Bulk Import
                        </button>
                        <button @click="addTrack" class="text-xs font-bold text-primary flex items-center gap-1">
                            <span class="material-symbols-outlined text-sm">add_circle</span>
                            Track toevoegen
                        </button>
                    </div>
                </div>
                
                <div class="space-y-4">
                    <div v-for="(tracks, disc) in editTracksByDisc" :key="disc" class="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-100 dark:border-slate-800">
                        <div class="flex items-center gap-2 mb-3">
                            <span class="text-[10px] font-black uppercase text-slate-400">Disc {{ disc }}</span>
                            <input v-model="tracks[0].disc_name" placeholder="Naam" class="text-[10px] font-bold bg-transparent border-b border-transparent focus:border-primary uppercase text-slate-500">
                        </div>
                        <div class="space-y-2">
                            <div v-for="track in tracks" :key="track._originalIndex" class="flex gap-2 items-center">
                                <input v-model.number="track.track_no" type="number" class="w-8 text-center bg-white dark:bg-slate-800 rounded p-1 text-xs border-none focus:ring-1 focus:ring-primary font-bold">
                                <input v-model="track.title" placeholder="Titel" class="flex-1 bg-white dark:bg-slate-800 rounded p-1 text-xs border-none focus:ring-1 focus:ring-primary font-medium">
                                <input v-model="track.duration" placeholder="0:00" class="w-12 bg-white dark:bg-slate-800 rounded p-1 text-[10px] border-none focus:ring-1 focus:ring-primary text-slate-500">
                                <button @click="removeTrack(track._originalIndex)" class="text-slate-300 hover:text-red-500">
                                    <span class="material-symbols-outlined text-sm">delete</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="flex gap-3 pt-2">
                <button @click="isEditing = false" class="flex-1 py-3 text-slate-500 font-bold hover:bg-slate-100 rounded-xl">Annuleren</button>
                <button @click="saveChanges" class="flex-1 py-3 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/30">Opslaan</button>
            </div>
        </div>

        <!-- TRACKLIST VIEW -->
        <div v-if="!isEditing">
            <h3 class="font-bold text-slate-900 dark:text-white text-sm uppercase tracking-wide mb-3">Tracklist</h3>
            <div class="space-y-4">
                <div v-for="(tracks, disc) in viewTracksByDisc" :key="disc" class="bg-white dark:bg-surface-dark rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800 overflow-hidden">
                    <div class="bg-slate-50 dark:bg-slate-800/50 px-4 py-2 flex items-center justify-between border-b border-slate-100 dark:border-slate-800">
                        <span class="text-[10px] font-black uppercase text-slate-500 tracking-wider">Disc {{ disc }}</span>
                        <span v-if="tracks[0].disc_name" class="text-[10px] font-bold uppercase text-primary">{{ tracks[0].disc_name }}</span>
                    </div>
                    <div class="divide-y divide-slate-100 dark:divide-slate-800">
                        <div v-for="track in tracks" :key="track.track_no" class="py-0.5 px-4 flex items-center gap-3 group">
                            <span class="text-xs font-bold text-slate-300 w-4">{{ track.track_no }}</span>
                            <span class="flex-1 font-medium text-slate-700 dark:text-slate-200 text-sm group-hover:text-primary transition-colors">{{ track.title }}</span>
                            <div class="flex items-center gap-3">
                                <a 
                                    :href="getLyricsUrl(track.title)" 
                                    target="_blank"
                                    class="p-1.5 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-300 hover:text-primary transition-all opacity-0 group-hover:opacity-100"
                                    title="Zoek lyrics"
                                >
                                    <span class="material-symbols-outlined text-base">description</span>
                                </a>
                                <span v-if="track.duration" class="text-[10px] font-mono text-slate-400">{{ track.duration }}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="!album.tracks || album.tracks.length === 0" class="bg-white dark:bg-surface-dark rounded-2xl p-8 border border-slate-100 dark:border-slate-800 flex flex-col items-center gap-2 text-slate-400">
                    <span class="material-symbols-outlined text-4xl opacity-30">playlist_play</span>
                    <p class="text-xs italic">Geen tracks bekend.</p>
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

  <!-- Bulk Import Modal -->
  <div v-if="showBulkModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 text-left">
    <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="showBulkModal = false"></div>
    <div class="relative w-full max-w-lg bg-white dark:bg-surface-dark rounded-3xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">
        <div class="p-6 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <h3 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <span class="material-symbols-outlined text-primary">format_list_bulleted_add</span>
                Bulk Tracks Importeren
            </h3>
            <button @click="showBulkModal = false" class="size-8 flex items-center justify-center rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                <span class="material-symbols-outlined text-slate-400">close</span>
            </button>
        </div>

        <div class="p-6 overflow-y-auto space-y-6 flex-1">
            <div class="space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-2">CSV Tekst Plakken</label>
                    <div class="mb-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-[10px] text-blue-700 dark:text-blue-300">
                        Formaat: <code>tracknr, titel, tijdsduur</code> per regel
                    </div>
                    <textarea 
                        v-model="bulkText" 
                        @input="handleBulkParse()"
                        rows="6" 
                        class="w-full p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border-none text-sm font-mono focus:ring-2 focus:ring-primary dark:text-white"
                        placeholder="1, Bohemian Rhapsody, 05:55&#10;2, Another One Bites the Dust, 03:34"
                    ></textarea>
                </div>

                <div class="relative">
                    <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-100 dark:border-slate-800"></div></div>
                    <div class="relative flex justify-center text-xs uppercase font-bold text-slate-400 bg-white dark:bg-surface-dark px-2">Of Bestand Uploaden</div>
                </div>

                <div>
                    <input 
                        type="file" 
                        accept=".txt" 
                        @change="handleBulkParse"
                        class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
                    >
                </div>
            </div>

            <!-- Preview Table -->
            <div v-if="parsedPreview.length > 0" class="space-y-3">
                <label class="block text-xs font-bold text-slate-500 uppercase">Voorbeeld Resultaat ({{ parsedPreview.length }} tracks)</label>
                <div class="border border-slate-100 dark:border-slate-800 rounded-xl overflow-hidden">
                    <table class="w-full text-left text-xs">
                        <thead class="bg-slate-50 dark:bg-slate-800/50">
                            <tr>
                                <th class="p-2 font-bold text-slate-400 w-8">#</th>
                                <th class="p-2 font-bold text-slate-400">Titel</th>
                                <th class="p-2 font-bold text-slate-400 w-16">Duur</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                            <tr v-for="t in parsedPreview" :key="t.position">
                                <td class="p-2 font-mono text-slate-400">{{ t.position }}</td>
                                <td class="p-2 font-medium text-slate-900 dark:text-white">{{ t.title }}</td>
                                <td class="p-2 text-slate-500">{{ t.duration || '--:--' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div v-if="bulkError" class="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-xs font-bold">
                {{ bulkError }}
            </div>

            <div v-if="isParsing" class="flex items-center justify-center py-8">
                <div class="animate-spin h-8 w-8 border-4 border-primary/20 border-t-primary rounded-full"></div>
            </div>
        </div>

        <div class="p-6 bg-slate-50 dark:bg-slate-800/50 flex gap-3">
            <button @click="showBulkModal = false" class="flex-1 py-3 text-slate-500 font-bold hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-colors">Annuleren</button>
            <button 
                @click="confirmBulkImport" 
                :disabled="parsedPreview.length === 0"
                class="flex-1 py-3 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/30 disabled:opacity-50 disabled:shadow-none"
            >
                Tracks Importeren
            </button>
        </div>
    </div>
  </div>
</template>
