<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <nav class="fixed bottom-0 left-0 right-0 border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-surface-dark/95 backdrop-blur-md pb-safe z-40">
    <div class="flex items-center justify-around p-2">
      
      <!-- Home -->
      <RouterLink to="/" 
        class="flex flex-col items-center gap-1 p-2 min-w-[64px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors" 
        active-class="text-primary font-bold">
        <span class="material-symbols-outlined" :class="{ 'icon-filled': $route.path === '/' }">home</span>
        <span class="text-[10px]">Home</span>
      </RouterLink>

      <!-- Search -->
      <RouterLink to="/collection" 
        class="flex flex-col items-center gap-1 p-2 min-w-[64px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors" 
        active-class="text-primary font-bold">
        <span class="material-symbols-outlined">search</span>
        <span class="text-[10px]">Zoeken</span>
      </RouterLink>

      <!-- ADD (Floating) -->
      <RouterLink to="/scan" class="relative -top-6 flex size-14 items-center justify-center rounded-full bg-primary text-white shadow-lg shadow-primary/40 active:scale-95 transition-transform border-4 border-background-light dark:border-background-dark">
        <span class="material-symbols-outlined text-[28px]">add</span>
      </RouterLink>

      <!-- Library (Locations) -->
      <RouterLink to="/locations" 
        class="flex flex-col items-center gap-1 p-2 min-w-[64px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors" 
        active-class="text-primary font-bold">
        <span class="material-symbols-outlined">grid_view</span>
        <span class="text-[10px]">Locaties</span>
      </RouterLink>

      <!-- Settings -->
      <button class="flex flex-col items-center gap-1 p-2 min-w-[64px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
        <span class="material-symbols-outlined">settings</span>
        <span class="text-[10px]">Settings</span>
      </button>

    </div>
  </nav>
</template>

<style scoped>
.pb-safe {
    padding-bottom: env(safe-area-inset-bottom);
}
</style>
