<script setup lang="ts">
import { ref } from 'vue'
import BarcodeScanner from '../components/BarcodeScanner.vue'

const activeTab = ref<'scan' | 'manual'>('scan')
const scannedCode = ref('')
const manualCode = ref('')
const loading = ref(false)
const error = ref('')
const albumData = ref<any>(null)

async function startLookup(code: string) {
    loading.value = true
    error.value = ''
    albumData.value = null
    scannedCode.value = code
    
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/lookup/${code}`)
        if (!response.ok) {
            if (response.status === 404) throw new Error('Album niet gevonden in de database.')
            throw new Error('Er ging iets mis bij het zoeken.')
        }
        albumData.value = await response.json()
    } catch (err) {
        error.value = err instanceof Error ? err.message : 'Onbekende fout'
    } finally {
        loading.value = false
    }
}

function handleScan(code: string) {
    startLookup(code)
}

function handleManualSearch() {
    if (manualCode.value) {
        startLookup(manualCode.value)
    }
}

async function saveAlbum() {
    if (!albumData.value) return
    
    loading.value = true
    try {
        // Stap 1: Maak album aan
        const response = await fetch(`${import.meta.env.VITE_API_URL}/albums/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: albumData.value.title,
                year: albumData.value.year,
                upc_ean: scannedCode.value,
                catalog_no: albumData.value.catalog_no,
                cover_url: albumData.value.cover_url
            })
        })
        
        if (response.ok) {
            alert('Album succesvol toegevoegd!')
            reset()
        }
    } catch (err) {
        error.value = 'Fout bij opslaan.'
    } finally {
        loading.value = false
    }
}

function reset() {
    scannedCode.value = ''
    manualCode.value = ''
    albumData.value = null
    error.value = ''
}
</script>

<template>
  <div class="w-full max-w-md mx-auto p-4 flex flex-col gap-6">
    
    <div class="flex items-center justify-between">
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">CD Toevoegen</h1>
        <button v-if="scannedCode" @click="reset" class="text-sm text-primary font-bold">Annuleren</button>
    </div>

    <!-- Tabs -->
    <div v-if="!scannedCode" class="flex p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
        <button 
            @click="activeTab = 'scan'"
            class="flex-1 py-2 text-sm font-medium rounded-lg transition-all"
            :class="activeTab === 'scan' ? 'bg-white dark:bg-surface-dark shadow text-primary' : 'text-slate-500 hover:text-slate-700'"
        >
            Scan Barcode
        </button>
        <button 
            @click="activeTab = 'manual'"
            class="flex-1 py-2 text-sm font-medium rounded-lg transition-all"
            :class="activeTab === 'manual' ? 'bg-white dark:bg-surface-dark shadow text-primary' : 'text-slate-500 hover:text-slate-700'"
        >
            Handmatig
        </button>
    </div>

    <!-- SCANNING STATE -->
    <div v-if="!scannedCode">
        <div v-if="activeTab === 'scan'" class="bg-slate-200 dark:bg-slate-800 rounded-xl min-h-[300px] flex flex-col items-center justify-center overflow-hidden">
            <BarcodeScanner @scan-success="handleScan" />
        </div>
        <div v-else class="flex flex-col gap-4">
            <div class="flex flex-col gap-2">
                <label class="text-sm font-medium text-slate-700 dark:text-slate-300">Barcode (EAN/UPC)</label>
                <div class="flex gap-2">
                    <input v-model="manualCode" type="text" placeholder="bijv. 07777463922" class="flex-1 rounded-lg border-slate-300 dark:bg-surface-dark dark:border-slate-700">
                    <button @click="handleManualSearch" class="bg-primary text-white px-4 py-2 rounded-lg font-medium">Zoek</button>
                </div>
            </div>
        </div>
    </div>

    <!-- RESULT STATE -->
    <div v-else class="flex flex-col gap-6">
        <div v-if="loading" class="flex flex-col items-center py-12">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p class="mt-4 text-slate-500">Informatie ophalen...</p>
        </div>

        <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 p-4 rounded-xl text-center">
            <span class="material-symbols-outlined text-red-500 text-4xl mb-2">error</span>
            <p class="text-red-700 dark:text-red-400 font-medium">{{ error }}</p>
            <button @click="reset" class="mt-4 text-sm font-bold text-slate-600 underline">Probeer opnieuw</button>
        </div>

        <div v-else-if="albumData" class="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4">
            <!-- Album Card Preview -->
            <div class="bg-white dark:bg-surface-dark rounded-2xl p-4 shadow-sm border border-slate-100 dark:border-slate-800 flex gap-4">
                <div class="size-24 shrink-0 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center overflow-hidden relative">
                    <img v-if="albumData.cover_url" :src="albumData.cover_url" class="w-full h-full object-cover" alt="Cover">
                    <span v-else class="material-symbols-outlined text-slate-400 text-4xl">album</span>
                </div>
                <div class="flex flex-col justify-center">
                    <h2 class="text-xl font-bold leading-tight">{{ albumData.title }}</h2>
                    <p class="text-slate-500 font-medium">{{ albumData.artists.join(', ') }}</p>
                    <p class="text-sm text-slate-400 mt-1">{{ albumData.year }} • {{ albumData.catalog_no || 'Geen catalogusnr' }}</p>
                </div>
            </div>

            <!-- Additional Fields -->
            <div class="flex flex-col gap-4">
                <h3 class="font-bold text-slate-900 dark:text-white">Details toevoegen</h3>
                <div class="flex flex-col gap-3">
                    <button class="flex items-center justify-between p-4 bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-slate-700">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-slate-400">location_on</span>
                            <span class="font-medium">Locatie selecteren</span>
                        </div>
                        <span class="material-symbols-outlined text-slate-400">chevron_right</span>
                    </button>
                    <button class="flex items-center justify-between p-4 bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-slate-700">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined text-slate-400">label</span>
                            <span class="font-medium">Tags toevoegen</span>
                        </div>
                        <span class="material-symbols-outlined text-slate-400">chevron_right</span>
                    </button>
                </div>
            </div>

            <button @click="saveAlbum" class="w-full py-4 bg-primary text-white rounded-2xl font-bold shadow-lg shadow-primary/30 active:scale-[0.98] transition-transform">
                Toevoegen aan Collectie
            </button>
        </div>
    </div>

  </div>
</template>
