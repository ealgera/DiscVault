<script setup lang="ts">
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100 antialiased pb-24">
    
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-background-light/95 dark:bg-background-dark/95 backdrop-blur-sm border-b border-slate-200 dark:border-slate-800 px-4 py-3 flex items-center justify-between transition-colors duration-200">
      <div class="flex items-center gap-3">
        <button class="flex items-center justify-center p-2 -ml-2 rounded-full hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors">
          <span class="material-symbols-outlined text-slate-900 dark:text-white">menu</span>
        </button>
        <div class="flex items-center gap-2">
          <div class="size-8 rounded-full bg-primary flex items-center justify-center">
            <span class="material-symbols-outlined text-white text-[20px]">album</span>
          </div>
          <h1 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">DiscVault</h1>
        </div>
      </div>
      <div class="flex items-center">
        <!-- Placeholder Avatar -->
        <button class="relative rounded-full overflow-hidden size-10 border-2 border-white dark:border-slate-700 shadow-sm bg-gray-300">
           <!-- Tijdelijk geen externe image om 404s te voorkomen, of we gebruiken een placeholder service -->
           <span class="flex items-center justify-center h-full w-full text-gray-600 font-bold">U</span>
        </button>
      </div>
    </header>

    <RouterView />
    <NavBar />
  </div>
</template>