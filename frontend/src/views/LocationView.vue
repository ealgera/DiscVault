<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Location {
  id: number
  name: string
  storage_type: string
  section?: string
  shelf?: string
  // albums?: any[] // Later kunnen we hier het aantal albums tonen
}

const locations = ref<Location[]>([])
const loading = ref(true)
const error = ref('')

// Form state

const showAddForm = ref(false)

const editingLocationId = ref<number | null>(null)

const newLocation = ref({

    name: '',

    storage_type: 'Kast',

    section: '',

    shelf: ''

})



async function fetchLocations() {

    loading.value = true

    try {

        const response = await fetch(`${import.meta.env.VITE_API_URL}/locations/`)

        if (response.ok) {

            locations.value = await response.json()

        }

    } catch (e) {

        error.value = 'Kon locaties niet laden.'

    } finally {

        loading.value = false

    }

}



function startEdit(loc: Location) {

    newLocation.value = { ...loc, section: loc.section || '', shelf: loc.shelf || '' }

    editingLocationId.value = loc.id

    showAddForm.value = true

    window.scrollTo({ top: 0, behavior: 'smooth' })

}



function resetForm() {

    newLocation.value = { name: '', storage_type: 'Kast', section: '', shelf: '' }

    editingLocationId.value = null

    showAddForm.value = false

}



async function saveLocation() {

    if (!newLocation.value.name) return



    try {

        let url = `${import.meta.env.VITE_API_URL}/locations/`

        let method = 'POST'



        if (editingLocationId.value) {

            url += `${editingLocationId.value}`

            method = 'PUT'

        }



        const response = await fetch(url, {

            method: method,

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify(newLocation.value)

        })

        

        if (response.ok) {

            await fetchLocations() // Refresh list

            resetForm()

        }

    } catch (e) {

        alert('Fout bij opslaan locatie')

    }

}



onMounted(() => {

    fetchLocations()

})

</script>



<template>



  <div class="p-4 max-w-md mx-auto pb-24">



    



        <!-- Sub Nav -->



    



        <div class="flex gap-4 mb-6 border-b border-slate-200 dark:border-slate-800">



    



            <router-link to="/locations" class="pb-2 text-sm font-bold border-b-2 border-primary text-primary">Locaties</router-link>



    



            <router-link to="/tags" class="pb-2 text-sm font-medium text-slate-400 hover:text-slate-600">Tags</router-link>



    



            <router-link to="/genres" class="pb-2 text-sm font-medium text-slate-400 hover:text-slate-600">Genres</router-link>



    



        </div>



    



    







    <div class="flex justify-between items-center mb-6">





        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Locaties</h1>

        <button @click="showAddForm ? resetForm() : (showAddForm = true)" class="bg-primary text-white px-4 py-2 rounded-lg text-sm font-bold shadow-sm">

            {{ showAddForm ? 'Annuleren' : '+ Nieuw' }}

        </button>

    </div>



    <!-- ADD/EDIT FORM -->

    <div v-if="showAddForm" class="bg-white dark:bg-surface-dark p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 mb-6 animate-in slide-in-from-top-2">

        <h2 class="font-bold mb-4 dark:text-white">{{ editingLocationId ? 'Wijzig Locatie' : 'Nieuwe Locatie' }}</h2>

        <form @submit.prevent="saveLocation" class="flex flex-col gap-3">

            <div>

                <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Naam (bijv. Woonkamer)</label>

                <input v-model="newLocation.name" type="text" class="w-full rounded-lg border-slate-300 dark:bg-slate-800 dark:border-slate-600 dark:text-white" required placeholder="Naam">

            </div>

            

            <div class="grid grid-cols-2 gap-3">

                <div>

                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Type</label>

                    <select v-model="newLocation.storage_type" class="w-full rounded-lg border-slate-300 dark:bg-slate-800 dark:border-slate-600 dark:text-white">

                        <option>Kast</option>

                        <option>Doos</option>

                        <option>Krat</option>

                        <option>Plank</option>

                        <option>Overig</option>

                    </select>

                </div>

                <div>

                    <label class="block text-xs font-bold text-slate-500 uppercase mb-1">Plank/Sectie</label>

                    <input v-model="newLocation.shelf" type="text" class="w-full rounded-lg border-slate-300 dark:bg-slate-800 dark:border-slate-600 dark:text-white" placeholder="Optioneel">

                </div>

            </div>



            <button type="submit" class="bg-primary text-white py-3 rounded-lg font-bold mt-2">{{ editingLocationId ? 'Opslaan' : 'Toevoegen' }}</button>

        </form>

    </div>



    <!-- LIST -->

    <div v-if="loading" class="text-center py-8">Laden...</div>

    <div v-else class="flex flex-col gap-3">

        <div v-for="loc in locations" :key="loc.id" @click="startEdit(loc)" class="bg-white dark:bg-surface-dark p-4 rounded-xl border border-slate-100 dark:border-slate-800 flex items-center gap-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800 transition">

            <div class="size-12 rounded-full bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center text-primary">

                <span class="material-symbols-outlined" v-if="loc.storage_type === 'Doos'">inventory_2</span>

                <span class="material-symbols-outlined" v-else>shelves</span>

            </div>

            <div>

                <h3 class="font-bold text-slate-900 dark:text-white">{{ loc.name }}</h3>

                <p class="text-sm text-slate-500">{{ loc.storage_type }} <span v-if="loc.shelf">• {{ loc.shelf }}</span></p>

            </div>

            <div class="ml-auto text-slate-300">

                <span class="material-symbols-outlined">edit</span>

            </div>

        </div>



        <div v-if="locations.length === 0" class="text-center text-slate-400 py-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-dashed border-slate-300 dark:border-slate-700">

            Nog geen locaties. Maak er eentje aan!

        </div>

    </div>



  </div>

</template>
