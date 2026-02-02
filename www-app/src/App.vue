<template>
  <div id="app">
    <AppHeader />
    <main class="app-main">
      <RouterView />
    </main>
    <LoginModal v-model="showLoginModal" />
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { RouterView } from 'vue-router';
import AppHeader from '@/components/organisms/AppHeader.vue';
import LoginModal from '@/components/organisms/LoginModal.vue';
import { useLoginModal } from '@/composables/useLoginModal';
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();
const { showLoginModal, close: closeLoginModal } = useLoginModal();

// Close login modal if user becomes authenticated
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated && showLoginModal.value) {
    closeLoginModal();
  }
});
</script>

<style scoped>
.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}
</style>
