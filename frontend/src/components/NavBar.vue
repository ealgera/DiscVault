<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg pb-safe">
    <div class="flex justify-around items-center h-16">
      
      <!-- Home -->
      <RouterLink to="/" class="flex flex-col items-center justify-center w-full h-full text-gray-500 hover:text-indigo-600" active-class="text-indigo-600 font-medium">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
        <span class="text-xs mt-1">Home</span>
      </RouterLink>

      <!-- Collectie -->
      <RouterLink to="/collection" class="flex flex-col items-center justify-center w-full h-full text-gray-500 hover:text-indigo-600" active-class="text-indigo-600 font-medium">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
        <span class="text-xs mt-1">Collectie</span>
      </RouterLink>

      <!-- Scan (Centraal/Groot) -->
      <RouterLink to="/scan" class="flex flex-col items-center justify-center w-full h-full">
        <div class="bg-indigo-600 text-white p-3 rounded-full -mt-6 shadow-lg border-4 border-gray-50">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
        </div>
        <span class="text-xs mt-1 font-medium text-gray-600">Scan</span>
      </RouterLink>

      <!-- Locaties -->
      <RouterLink to="/locations" class="flex flex-col items-center justify-center w-full h-full text-gray-500 hover:text-indigo-600" active-class="text-indigo-600 font-medium">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg> <!-- Tijdelijk zelfde icoon, later aanpassen -->
        <span class="text-xs mt-1">Locaties</span>
      </RouterLink>

    </div>
  </nav>
</template>

<style scoped>
.pb-safe {
    padding-bottom: env(safe-area-inset-bottom);
}
</style>
