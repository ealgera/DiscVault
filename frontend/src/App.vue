<script setup lang="ts">
import { RouterView } from 'vue-router'
import NavBar from './components/NavBar.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-slate-900 pb-20"> <!-- Padding bottom voor navbar ruimte -->
    <RouterView />
    <NavBar />
  </div>
</template>
