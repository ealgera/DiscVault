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

async function fetchMetadata() {
    try {
        const [locRes, tagRes, constRes] = await Promise.all([
            fetch(`${import.meta.env.VITE_API_URL}/locations/`),
            fetch(`${import.meta.env.VITE_API_URL}/tags/`),
            fetch(`${import.meta.env.VITE_API_URL}/constants`)
        ])
        if (locRes.ok) locations.value = await locRes.json()
        if (tagRes.ok) allTags.value = await tagRes.json()
        if (constRes.ok) {
            const constants = await constRes.json()
            mediaTypes.value = constants.media_types
        }
    } catch(e) { console.error(e) }
}

async function startCamera() {
    error.value = ''
    scannedCode.value = ''
    albumData.value = null
    selectedTagIds.value = []
    selectedLocationId.value = null
    mediaType.value = 'CD' // Reset to default
    
    // Load metadata if needed
    if (mediaTypes.value.length === 0) await fetchMetadata()
    
    isCameraActive.value = true
    
    await nextTick()

    try {
        scanner.value = new Html5Qrcode(cameraId)
        await scanner.value.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: { width: 250, height: 250 } },
            (decodedText) => {
                handleScan(decodedText)
            },
            (errorMessage) => {
                // ignore errors during scanning
            }
        )
    } catch (err) {
        error.value = "Kon camera niet starten. Zorg voor HTTPS of localhost."
        isCameraActive.value = false
    }
}

async function stopCamera() {
    if (scanner.value && scanner.value.isScanning) {
        await scanner.value.stop()
        scanner.value = null
    }
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
        // Fetch metadata (locations/tags) if not loaded yet
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
    
    try {
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
                media_type: mediaType.value
            })
        })
        
        if (response.ok) {
            const newAlbum = await response.json()
            router.push(`/albums/${newAlbum.id}`)
        } else {
            alert("Opslaan mislukt")
        }
    } catch (e) {
        alert("Fout bij opslaan")
    }
}

// Cleanup
onUnmounted(() => {
    stopCamera()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-background-dark pb-20">
    <!-- Header -->
    <div class="p-4 bg-white dark:bg-surface-dark shadow-sm flex items-center gap-4">
        <button @click="router.back()" class="text-primary font-bold">Terug</button>
        <h1 class="text-lg font-bold flex-1 text-center">Scanner</h1>
        <div class="w-10"></div>
    </div>

    <!-- Camera Area -->
    <div v-if="isCameraActive" class="relative bg-black h-96 w-full flex items-center justify-center overflow-hidden">
        <div id="reader" class="w-full h-full"></div>
        <button @click="stopCamera" class="absolute top-4 right-4 bg-white/20 text-white p-2 rounded-full backdrop-blur-md z-10">
            <span class="material-symbols-outlined">close</span>
        </button>
    </div>

    <!-- Start/Manual Input Area -->
    <div v-else-if="!albumData && !loading" class="p-6 flex flex-col items-center gap-6 mt-10">
        <div class="w-20 h-20 bg-blue-50 dark:bg-blue-900/20 rounded-full flex items-center justify-center text-primary mb-4">
            <span class="material-symbols-outlined text-4xl">barcode_scanner</span>
        </div>
        
        <button @click="startCamera" class="w-full py-4 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/30 flex items-center justify-center gap-2">
            <span class="material-symbols-outlined">photo_camera</span>
            Start Camera
        </button>

        <div class="w-full border-t border-slate-200 dark:border-slate-800 my-2"></div>

        <div class="w-full">
            <label class="block text-xs font-bold text-slate-400 uppercase mb-2 text-center">Of voer barcode handmatig in</label>
            <div class="flex gap-2">
                <input v-model="scannedCode" type="text" class="flex-1 bg-white dark:bg-slate-800 border-none rounded-xl p-3 shadow-sm focus:ring-2 focus:ring-primary" placeholder="EAN / UPC">
                <button @click="fetchAlbumData(scannedCode)" class="bg-slate-200 dark:bg-slate-700 px-4 rounded-xl font-bold">
                    <span class="material-symbols-outlined">search</span>
                </button>
            </div>
        </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20 gap-4">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
        <p class="text-slate-500 font-bold animate-pulse">Gegevens ophalen...</p>
    </div>

    <!-- Error -->
    <div v-if="error" class="p-6 text-center">
        <div class="text-red-500 font-bold mb-4">{{ error }}</div>
        <button @click="error = ''; startCamera()" class="text-primary font-bold">Opnieuw proberen</button>
    </div>

    <!-- Result Preview -->
    <div v-if="albumData" class="p-6 animate-in slide-in-from-bottom-4">
        <div class="bg-white dark:bg-surface-dark rounded-2xl shadow-xl border border-slate-100 dark:border-slate-800 overflow-hidden">
            <!-- Cover Header -->
            <div class="h-32 bg-slate-100 dark:bg-slate-800 relative">
                <img v-if="albumData.cover_url" :src="albumData.cover_url" class="w-full h-full object-cover opacity-50 blur-sm">
                <div class="absolute -bottom-10 left-6">
                    <img v-if="albumData.cover_url" :src="albumData.cover_url" class="w-24 h-24 rounded-lg shadow-lg border-2 border-white dark:border-surface-dark object-cover bg-white">
                    <div v-else class="w-24 h-24 rounded-lg shadow-lg border-2 border-white bg-slate-200 flex items-center justify-center">
                        <span class="material-symbols-outlined text-3xl text-slate-400">album</span>
                    </div>
                </div>
            </div>

            <div class="pt-12 px-6 pb-6">
                <div class="mb-6">
                    <h2 class="text-xl font-bold leading-tight text-slate-900 dark:text-white">{{ albumData.title }}</h2>
                    <p class="text-primary font-bold">{{ albumData.artists.join(', ') }}</p>
                    <p class="text-sm text-slate-400 mt-1">{{ albumData.year }} • {{ albumData.catalog_no || 'Geen catalogusnr' }}</p>
                    <div class="flex flex-wrap gap-1 mt-2">
                        <span v-for="g in albumData.genres" :key="g" class="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded text-[10px] font-bold text-slate-500">
                            {{ g }}
                        </span>
                    </div>
                </div>

                <div class="space-y-4">
                    <!-- Media Type -->
                    <div>
                        <label class="block text-xs font-bold text-slate-500 uppercase mb-2">Media Type</label>
                        <select v-model="mediaType" class="w-full p-3 bg-slate-50 dark:bg-slate-800 rounded-xl border-none font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-primary">
                            <option v-for="t in mediaTypes" :key="t" :value="t">{{ t }}</option>
                        </select>
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
                </div>

                <div class="flex gap-3 mt-8">
                    <button @click="albumData = null; scannedCode = ''; mediaType = 'CD'" class="flex-1 py-3 text-slate-500 font-bold hover:bg-slate-50 rounded-xl">Annuleren</button>
                    <button @click="saveAlbum" class="flex-1 py-3 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/30">Opslaan</button>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>