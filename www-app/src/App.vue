<template>
  <div id="app">
    <AppHeader />
    <main class="app-main">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router';
import AppHeader from '@/components/organisms/AppHeader.vue';
import AppFooter from '@/components/organisms/AppFooter.vue';
</script>

<style scoped>
.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
