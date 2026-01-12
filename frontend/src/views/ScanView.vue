<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Html5Qrcode } from 'html5-qrcode'
import { useRouter } from 'vue-router'

const router = useRouter()
const scanner = ref<Html5Qrcode | null>(null)
const cameraId = "reader"

// State
const scannedCode = ref('')
const albumData = ref<any>(null)
const locations = ref<any[]>([])
const selectedLocationId = ref<number | null>(null)
const allTags = ref<any[]>([])
const selectedTagIds = ref<number[]>([])
const mediaType = ref('CD')

const mediaTypes = ref<string[]>([])

// Camera state
const isCameraActive = ref(false)
const error = ref('')
const loading = ref(false)
const cameras = ref<any[]>([])
const currentCameraIndex = ref(0)

const selectedFile = ref<File | null>(null)
const coverPreview = ref<string | null>(null)

const allGenres = ref<any[]>([])

async function fetchMetadata() {
    try {
        const [locRes, tagRes, genRes, constRes] = await Promise.all([
            fetch(`${import.meta.env.VITE_API_URL}/locations/`),
            fetch(`${import.meta.env.VITE_API_URL}/tags/`),
            fetch(`${import.meta.env.VITE_API_URL}/genres/`),
            fetch(`${import.meta.env.VITE_API_URL}/constants`)
        ])
        if (locRes.ok) locations.value = await locRes.json()
        if (tagRes.ok) allTags.value = await tagRes.json()
        if (genRes.ok) allGenres.value = await genRes.json()
        if (constRes.ok) {
            const constants = await constRes.json()
            mediaTypes.value = constants.media_types
        }
    } catch(e) { console.error(e) }
}

function manualAdd() {
    stopCamera()
    albumData.value = {
        title: '',
        artists: [],
        year: new Date().getFullYear(),
        genres: [],
        catalog_no: '',
        cover_url: '',
        media_type: 'CD',
        spars_code: '',
        notes: '',
        upc_ean: '',
        tracks: []
    }
    selectedTagIds.value = []
    selectedLocationId.value = null
    mediaType.value = 'CD'
    selectedFile.value = null
    coverPreview.value = null
}

function onCoverChange(e: any) {
    const file = e.target.files[0]
    if (file) {
        selectedFile.value = file
        coverPreview.value = URL.createObjectURL(file)
    }
}

async function getCameras() {
    try {
        const devices = await Html5Qrcode.getCameras()
        if (devices && devices.length) {
            // Filter out obviously front-facing cameras if possible, but keep them in the list to cycle through
            cameras.value = devices
            
            // Try to find a back camera to start with
            const backCameraIndex = devices.findIndex(c => c.label.toLowerCase().includes('back') || c.label.toLowerCase().includes('environment'))
            if (backCameraIndex !== -1) {
                currentCameraIndex.value = backCameraIndex
            } else {
                // If no clear back camera, usually the last one on Android is the main back camera
                currentCameraIndex.value = devices.length - 1
            }
        }
    } catch (e) {
        error.value = "Kon geen camera's vinden."
    }
}

async function startCamera() {
    error.value = ''
    scannedCode.value = ''
    albumData.value = null
    selectedTagIds.value = []
    selectedLocationId.value = null
    mediaType.value = 'CD'
    
    if (mediaTypes.value.length === 0) await fetchMetadata()
    if (cameras.value.length === 0) await getCameras()
    
    isCameraActive.value = true
    
    await nextTick()

    if (cameras.value.length === 0) {
        error.value = "Geen camera gevonden."
        return
    }

    startScannerInstance(cameras.value[currentCameraIndex.value].id)
}

async function startScannerInstance(deviceId: string) {
    try {
        // If scanner exists and is running, stop it first
        if (scanner.value) {
            if (scanner.value.isScanning) {
                await scanner.value.stop()
            }
        } else {
            scanner.value = new Html5Qrcode(cameraId)
        }

        await scanner.value.start(
            deviceId,
            { 
                fps: 10,
                // Full screen scanning
            },
            (decodedText) => {
                handleScan(decodedText)
            },
            (errorMessage) => {
                // ignore
            }
        )
    } catch (err) {
        error.value = "Kon camera niet starten. Probeer een andere."
        isCameraActive.value = false
    }
}

async function switchCamera() {
    if (cameras.value.length < 2) return
    
    currentCameraIndex.value = (currentCameraIndex.value + 1) % cameras.value.length
    await startScannerInstance(cameras.value[currentCameraIndex.value].id)
}

async function stopCamera() {
    if (scanner.value && scanner.value.isScanning) {
        await scanner.value.stop()
    }
    // Don't null the scanner instance here, we might reuse it. 
    // Actually, Html5Qrcode instance is tied to element ID.
    // If we destroy the element (v-if), we should probably recreate the instance next time.
    scanner.value = null
    isCameraActive.value = false
}

async function handleScan(barcode: string) {
    await stopCamera()
    scannedCode.value = barcode
    fetchAlbumData(barcode)
}

async function fetchAlbumData(barcode: string) {
    loading.value = true
    error.value = ''
    try {
        if (mediaTypes.value.length === 0) {
            await fetchMetadata()
        }

        const response = await fetch(`${import.meta.env.VITE_API_URL}/lookup/${barcode}`)
        if (response.ok) {
            albumData.value = await response.json()
        } else {
            error.value = "Album niet gevonden in MusicBrainz."
        }
    } catch (e) {
        error.value = "Fout bij ophalen gegevens."
    } finally {
        loading.value = false
    }
}

async function saveAlbum() {
    if (!albumData.value) return
    
    loading.value = true
    try {
        // 1. Create album first to get ID
        const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: albumData.value.title,
                year: albumData.value.year,
                upc_ean: scannedCode.value,
                catalog_no: albumData.value.catalog_no,
                cover_url: albumData.value.cover_url,
                location_id: selectedLocationId.value,
                tag_ids: selectedTagIds.value,
                artist_names: albumData.value.artists,
                genre_names: albumData.value.genres,
                media_type: mediaType.value,
                notes: albumData.value.notes,
                spars_code: albumData.value.spars_code,
                tracks: albumData.value.tracks
            })
        })
        
        if (response.ok) {
            const newAlbum = await response.json()

            // 2. Upload cover if exists
            if (selectedFile.value) {
                const formData = new FormData()
                formData.append('file', selectedFile.value)
                await fetch(`${import.meta.env.VITE_API_URL}/albums/${newAlbum.id}/cover`, {
                    method: 'POST',
                    body: formData
                })
            }

            router.push(`/albums/${newAlbum.id}`)
        } else {
            alert("Opslaan mislukt")
        }
    } catch (e) {
        alert("Fout bij opslaan")
    } finally {
        loading.value = false
    }
}

function resolveCoverURL(url: string | undefined) {
    if (!url) return undefined
    if (url.startsWith('http')) return url
    const baseUrl = import.meta.env.VITE_API_URL.replace(/\/$/, '')
    const path = url.startsWith('/') ? url : `/${url}`
    return `${baseUrl}${path}`
}

function addTrack() {
    if (!albumData.value.tracks) albumData.value.tracks = []
    const lastTrack = albumData.value.tracks[albumData.value.tracks.length - 1]
    const nextDisc = lastTrack ? lastTrack.disc_no : 1
    const nextNo = lastTrack ? lastTrack.track_no + 1 : 1
    
    albumData.value.tracks.push({
        track_no: nextNo,
        title: '',
        duration: '',
        disc_no: nextDisc,
        disc_name: lastTrack ? lastTrack.disc_name : 'Format'
    })
}

function removeTrack(index: number) {
    albumData.value.tracks.splice(index, 1)
}

const tracksByDisc = computed(() => {
    if (!albumData.value?.tracks) return {}
    return albumData.value.tracks.reduce((acc: any, track: any, index: number) => {
        const d = track.disc_no || 1
        if (!acc[d]) acc[d] = []
        // We add the original index but keep the original object reference
        track._originalIndex = index 
        acc[d].push(track)
        return acc
    }, {})
})

onMounted(() => {
    startCamera()
})

onUnmounted(() => {
    if (scanner.value && scanner.value.isScanning) {
        scanner.value.stop()
    }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-background-dark pb-20">
    <!-- Header -->
    <div class="p-4 bg-white dark:bg-surface-dark shadow-sm flex items-center gap-4 sticky top-0 z-20">
        <button @click="router.back()" class="text-primary font-bold flex items-center gap-1">
            <span class="material-symbols-outlined text-xl">arrow_back_ios_new</span>
            Terug
        </button>
        <h1 class="text-lg font-bold flex-1 text-center">Scanner</h1>
        <div class="w-16"></div> <!-- Spacer for balance -->
    </div>

    <!-- Camera Area -->
    <div v-if="isCameraActive" class="relative bg-black h-[50vh] w-full flex items-center justify-center overflow-hidden">
        <div id="reader" class="w-full h-full"></div>
        
        <!-- Overlay Guide -->
        <div class="absolute inset-0 pointer-events-none flex items-center justify-center">
            <div class="w-64 h-40 border-2 border-white/50 rounded-lg"></div>
        </div>

        <!-- Camera Controls -->
        <div class="absolute bottom-4 left-0 right-0 flex justify-center gap-6 pointer-events-auto z-10">
            <button v-if="cameras.length > 1" @click="switchCamera" class="bg-white/20 text-white p-3 rounded-full backdrop-blur-md hover:bg-white/30 transition">
                <span class="material-symbols-outlined">flip_camera_ios</span>
            </button>
        </div>

        <button @click="stopCamera" class="absolute top-4 right-4 bg-white/20 text-white p-2 rounded-full backdrop-blur-md z-10 pointer-events-auto">
            <span class="material-symbols-outlined">close</span>
        </button>
    </div>

    <!-- Manual Input Area (always visible when not loading result) -->
    <div v-if="!albumData && !loading" class="p-6 flex flex-col items-center gap-6">
        
        <div v-if="!isCameraActive" class="w-full text-center py-8 bg-slate-100 dark:bg-slate-800 rounded-xl" @click="startCamera">
            <span class="material-symbols-outlined text-4xl text-slate-400 mb-2">photo_camera</span>
            <p class="font-bold text-slate-500">Camera gestopt. Tik om te starten.</p>
        </div>

        <div class="w-full">
            <label class="block text-xs font-bold text-slate-400 uppercase mb-2 text-center">Of voer barcode handmatig in</label>
            <div class="flex gap-2 mb-4">
                <input v-model="scannedCode" type="text" class="flex-1 bg-white dark:bg-slate-800 border-none rounded-xl p-3 shadow-sm focus:ring-2 focus:ring-primary font-mono text-center tracking-widest" placeholder="EAN / UPC">
                <button @click="fetchAlbumData(scannedCode)" class="bg-slate-200 dark:bg-slate-700 px-4 rounded-xl font-bold hover:bg-slate-300 transition">
                    <span class="material-symbols-outlined font-bold">search</span>
                </button>
            </div>
            
            <button @click="manualAdd" class="w-full py-4 bg-white dark:bg-slate-800 border-2 border-dashed border-slate-200 dark:border-slate-700 rounded-xl text-slate-500 font-bold flex items-center justify-center gap-2 hover:border-primary hover:text-primary transition-colors">
                <span class="material-symbols-outlined">add_circle</span>
                Handmatig toevoegen
            </button>
        </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
        <p class="text-slate-500 font-bold animate-pulse">Gegevens ophalen...</p>
    </div>

    <!-- Error -->
    <div v-if="error" class="p-6 text-center animate-in fade-in">
        <div class="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-xl font-bold mb-4 border border-red-100 dark:border-red-900/30">
            {{ error }}
        </div>
        <button @click="startCamera" class="text-primary font-bold hover:underline">Opnieuw proberen</button>
    </div>

    <!-- Result Preview -->
    <div v-if="albumData" class="p-6 animate-in slide-in-from-bottom-4 pb-32">
        <div class="bg-white dark:bg-surface-dark rounded-2xl shadow-xl border border-slate-100 dark:border-slate-800 overflow-hidden">
            <!-- Cover Header -->
            <div class="h-32 bg-slate-100 dark:bg-slate-800 relative">
                <img v-if="coverPreview || albumData.cover_url" :src="coverPreview || resolveCoverURL(albumData.cover_url)" class="w-full h-full object-cover opacity-50 blur-sm">
                <div class="absolute -bottom-10 left-6">
                    <img v-if="coverPreview || albumData.cover_url" :src="coverPreview || resolveCoverURL(albumData.cover_url)" class="w-24 h-24 rounded-lg shadow-lg border-2 border-white dark:border-surface-dark object-cover bg-white">
                    <div v-else class="w-24 h-24 rounded-lg shadow-lg border-2 border-white bg-slate-200 flex items-center justify-center">
                        <span class="material-symbols-outlined text-3xl text-slate-400">album</span>
                    </div>
                </div>
            </div>

            <div class="pt-12 px-6 pb-6">
                <!-- Cover Upload -->
                <div class="mb-6 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-dashed border-slate-200 dark:border-slate-700">
                    <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Cover Afbeelding Aanpassen</label>
                    <input type="file" @change="onCoverChange" accept="image/*" class="text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20">
                </div>
                <!-- Editable Details -->
                <div class="space-y-4 mb-6">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Titel</label>
                        <input v-model="albumData.title" class="w-full p-2 bg-slate-50 dark:bg-slate-800 rounded-lg border-none font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-primary">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Artist(s) <span class="text-[10px] lowercase font-normal">(komma gescheiden)</span></label>
                        <input :value="albumData.artists.join(', ')" @input="(e:any) => albumData.artists = e.target.value.split(',').map((s:string) => s.trim())" class="w-full p-2 bg-slate-50 dark:bg-slate-800 rounded-lg border-none font-bold text-primary focus:ring-2 focus:ring-primary">
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Jaar</label>
                            <input v-model.number="albumData.year" type="number" class="w-full p-2 bg-slate-50 dark:bg-slate-800 rounded-lg border-none font-medium text-slate-600 focus:ring-2 focus:ring-primary">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Catalogus #</label>
                            <input v-model="albumData.catalog_no" class="w-full p-2 bg-slate-50 dark:bg-slate-800 rounded-lg border-none font-medium text-slate-600 focus:ring-2 focus:ring-primary">
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Barcode</label>
                        <input v-model="scannedCode" class="w-full p-2 bg-slate-50 dark:bg-slate-800 rounded-lg border-none font-mono text-sm text-slate-500 focus:ring-2 focus:ring-primary">
                    </div>
                </div>

                <div class="space-y-4">
                    <!-- Media Type -->
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Media Type</label>
                            <select v-model="mediaType" class="w-full p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border-none font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-primary">
                                <option v-for="t in mediaTypes" :key="t" :value="t">{{ t }}</option>
                            </select>
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-2">SPARS</label>
                            <input v-model="albumData.spars_code" class="w-full p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border-none font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-primary" placeholder="bijv. DDD">
                        </div>
                    </div>

                    <!-- Location -->
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Locatie (Optioneel)</label>
                        <select v-model="selectedLocationId" class="w-full p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border-none font-medium text-slate-900 dark:text-white focus:ring-2 focus:ring-primary">
                            <option :value="null">Kies locatie...</option>
                            <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                                {{ loc.name }} ({{ loc.storage_type }})
                            </option>
                        </select>
                    </div>

                    <!-- Genres -->
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Genres</label>
                        <div class="flex flex-wrap gap-2">
                            <button 
                                v-for="genre in allGenres" :key="genre.id"
                                @click="albumData.genres.includes(genre.name) ? albumData.genres = albumData.genres.filter((n:string) => n !== genre.name) : albumData.genres.push(genre.name)"
                                class="px-3 py-1.5 rounded-full text-xs font-bold border transition-all"
                                :class="albumData.genres.includes(genre.name) ? 'bg-slate-600 text-white border-slate-600 shadow-sm' : 'bg-slate-50 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700'"
                            >
                                {{ genre.name }}
                            </button>
                            <div class="flex items-center gap-1 ml-1">
                                <input @keyup.enter="(e:any) => { if (e.target.value) { albumData.genres.push(e.target.value); e.target.value = '' } }" placeholder="Nieuw..." class="w-20 p-1 text-xs bg-transparent border-b border-slate-300 dark:border-slate-600 focus:outline-none focus:border-primary">
                            </div>
                        </div>
                    </div>

                    <!-- Tags -->
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Tags</label>
                        <div class="flex flex-wrap gap-2">
                            <button 
                                v-for="tag in allTags" :key="tag.id"
                                @click="selectedTagIds.includes(tag.id) ? selectedTagIds = selectedTagIds.filter(id => id !== tag.id) : selectedTagIds.push(tag.id)"
                                class="px-3 py-1.5 rounded-full text-xs font-bold border transition-all"
                                :class="selectedTagIds.includes(tag.id) ? 'bg-primary text-white border-primary shadow-sm' : 'bg-slate-50 dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700'"
                                :style="selectedTagIds.includes(tag.id) ? { backgroundColor: tag.color, borderColor: tag.color } : {}"
                            >
                                {{ tag.name }}
                            </button>
                        </div>
                    </div>

                    <!-- Notes -->
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Notities</label>
                        <textarea v-model="albumData.notes" rows="2" class="w-full p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border-none text-sm text-slate-700 dark:text-slate-300 focus:ring-2 focus:ring-primary" placeholder="Eventuele opmerkingen..."></textarea>
                    </div>

                    <!-- Tracklist -->
                    <div>
                        <div class="flex items-center justify-between mb-2">
                            <label class="block text-xs font-bold text-slate-500 uppercase">Tracklist</label>
                            <button @click="addTrack" class="text-xs font-bold text-primary flex items-center gap-1">
                                <span class="material-symbols-outlined text-sm">add_circle</span>
                                Track toevoegen
                            </button>
                        </div>
                        
                        <div class="space-y-4">
                            <div v-for="(tracks, disc) in tracksByDisc" :key="disc" class="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-100 dark:border-slate-800">
                                <div class="flex items-center gap-2 mb-3">
                                    <span class="text-[10px] font-black uppercase text-slate-400">Disc {{ disc }}</span>
                                    <input v-model="tracks[0].disc_name" placeholder="Naam (bijv. CD1)" class="text-[10px] font-bold bg-transparent border-b border-transparent focus:border-primary uppercase text-slate-500">
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
                            <div v-if="!albumData.tracks || albumData.tracks.length === 0" class="text-center py-4 text-xs text-slate-400 italic">
                                Geen tracks toegevoegd.
                            </div>
                        </div>
                    </div>
                </div>

                <div class="flex gap-3 mt-8">
                    <button @click="albumData = null; scannedCode = ''; startCamera()" class="flex-1 py-3 text-slate-500 font-bold hover:bg-slate-50 rounded-xl">Annuleren</button>
                    <button @click="saveAlbum" class="flex-1 py-3 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/30">Opslaan</button>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>