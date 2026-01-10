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
            <div class="flex gap-2">
                <input v-model="scannedCode" type="text" class="flex-1 bg-white dark:bg-slate-800 border-none rounded-xl p-3 shadow-sm focus:ring-2 focus:ring-primary font-mono text-center tracking-widest" placeholder="EAN / UPC">
                <button @click="fetchAlbumData(scannedCode)" class="bg-slate-200 dark:bg-slate-700 px-4 rounded-xl font-bold hover:bg-slate-300 transition">
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
                    <button @click="albumData = null; scannedCode = ''; startCamera()" class="flex-1 py-3 text-slate-500 font-bold hover:bg-slate-50 rounded-xl">Annuleren</button>
                    <button @click="saveAlbum" class="flex-1 py-3 bg-primary text-white rounded-xl font-bold shadow-lg shadow-primary/30">Opslaan</button>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>