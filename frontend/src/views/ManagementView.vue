<script setup lang="ts">
import { ref } from 'vue'

const exporting = ref(false)
const importing = ref(false)
const message = ref('')
const error = ref('')
const selectedFile = ref<File | null>(null)
const importSuccess = ref(false)

async function exportCollection() {
    exporting.value = true
    error.value = ''
    message.value = 'Backup wordt voorbereid...'
    
    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/export`)
        if (response.ok) {
            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            
            // Get filename from header if possible
            const contentDisposition = response.headers.get('Content-Disposition')
            let filename = 'discvault_backup.zip'
            if (contentDisposition && contentDisposition.includes('filename=')) {
                filename = contentDisposition.split('filename=')[1].replace(/"/g, '')
            }
            
            a.download = filename
            document.body.appendChild(a)
            a.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(a)
            message.value = 'Backup succesvol gedownload!'
        } else {
            error.value = 'Export mislukt.'
        }
    } catch (e) {
        error.value = 'Fout bij verbinden met server.'
    } finally {
        exporting.value = false
    }
}

function onFileChange(e: any) {
    selectedFile.value = e.target.files[0]
    importSuccess.value = false
    error.value = ''
}

async function importCollection() {
    if (!selectedFile.value) return
    
    if (!confirm('WEET JE HET ZEKER? Dit overschrijft je huidige collectie volledig met de data uit de backup!')) {
        return
    }
    
    importing.value = true
    error.value = ''
    message.value = 'Backup wordt hersteld...'
    
    try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        
        const response = await fetch(`${import.meta.env.VITE_API_URL}/import`, {
            method: 'POST',
            body: formData
        })
        
        const result = await response.json()
        if (response.ok) {
            importSuccess.value = true
            message.value = result.message
        } else {
            error.value = result.detail || 'Import mislukt.'
        }
    } catch (e) {
        error.value = 'Fout bij verbinding met server.'
    } finally {
        importing.value = false
    }
}
</script>

<template>
    <div class="p-6 pb-32 max-w-2xl mx-auto">
        <h1 class="text-2xl font-black text-slate-900 dark:text-white mb-8 flex items-center gap-3">
            <span class="material-symbols-outlined text-primary text-3xl">settings</span>
            Beheer & Back-up
        </h1>

        <div class="space-y-6">
            <!-- Export Section -->
            <section class="bg-white dark:bg-surface-dark p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                <div class="flex items-center gap-4 mb-4">
                    <div class="p-3 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 rounded-xl">
                        <span class="material-symbols-outlined">file_download</span>
                    </div>
                    <div>
                        <h2 class="font-bold text-slate-900 dark:text-white">Collectie Exporteren</h2>
                        <p class="text-xs text-slate-500">Download je volledige database en alle covers in één ZIP-bestand.</p>
                    </div>
                </div>
                
                <button 
                    @click="exportCollection" 
                    :disabled="exporting || importing"
                    class="w-full py-3 bg-primary text-white font-bold rounded-xl shadow-lg shadow-primary/30 active:scale-95 transition-all disabled:opacity-50 disabled:scale-100"
                >
                    <span v-if="exporting" class="flex items-center justify-center gap-2">
                        <div class="animate-spin h-4 w-4 border-2 border-white/30 border-t-white rounded-full"></div>
                        Exporteren...
                    </span>
                    <span v-else>Download ZIP Back-up</span>
                </button>
            </section>

            <!-- Import Section -->
            <section class="bg-white dark:bg-surface-dark p-6 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-800">
                <div class="flex items-center gap-4 mb-4">
                    <div class="p-3 bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 rounded-xl">
                        <span class="material-symbols-outlined">file_upload</span>
                    </div>
                    <div>
                        <h2 class="font-bold text-slate-900 dark:text-white">Collectie Herstellen</h2>
                        <p class="text-xs text-slate-500">Herstel je collectie vanuit een eerder gemaakte ZIP back-up.</p>
                    </div>
                </div>

                <div class="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 p-4 rounded-xl mb-4">
                    <p class="text-[10px] text-red-600 dark:text-red-400 uppercase font-black mb-1">Waarschuwing</p>
                    <p class="text-xs text-red-800 dark:text-red-300">
                        Dit overschrijft AL je huidige gegevens. Zorg dat je zeker weet dat je de juiste backup hebt.
                    </p>
                </div>

                <div class="mb-4">
                    <input 
                        type="file" 
                        accept=".zip" 
                        @change="onFileChange"
                        class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
                    >
                </div>

                <button 
                    @click="importCollection" 
                    :disabled="!selectedFile || importing || exporting"
                    class="w-full py-3 bg-slate-900 dark:bg-slate-700 text-white font-bold rounded-xl shadow-lg active:scale-95 transition-all disabled:opacity-30 disabled:scale-100"
                >
                    <span v-if="importing" class="flex items-center justify-center gap-2">
                        <div class="animate-spin h-4 w-4 border-2 border-white/30 border-t-white rounded-full"></div>
                        Bezig met herstellen...
                    </span>
                    <span v-else>Herstel vanaf ZIP</span>
                </button>
            </section>

            <!-- Status Messages -->
            <div v-if="message && !error" class="bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-900/30 p-4 rounded-xl animate-in fade-in slide-in-from-top-2">
                <div class="flex items-center gap-2 text-green-700 dark:text-green-400 font-bold text-sm">
                    <span class="material-symbols-outlined">check_circle</span>
                    {{ message }}
                </div>
            </div>

            <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 p-4 rounded-xl animate-in fade-in slide-in-from-top-2">
                <div class="flex items-center gap-2 text-red-700 dark:text-red-400 font-bold text-sm">
                    <span class="material-symbols-outlined">error</span>
                    {{ error }}
                </div>
            </div>

            <div v-if="importSuccess" class="bg-primary/10 border border-primary/20 p-6 rounded-2xl text-center shadow-inner">
                <h3 class="font-black text-primary mb-2">IMPORT VOLTOOID</h3>
                <p class="text-sm text-slate-600 dark:text-slate-400 mb-4 text-balance">
                    De database en covers zijn succesvol hersteld. Herlaad de app om alles te zien.
                </p>
                <button @click="window.location.reload()" class="px-6 py-2 bg-primary text-white font-bold rounded-full text-sm">
                    App Nu Herladen
                </button>
            </div>
        </div>
    </div>
</template>
