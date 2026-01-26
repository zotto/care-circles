<template>
  <div class="auth-callback-view">
    <div class="callback-container">
      <div class="callback-card">
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <h2 class="loading-title">Signing you in...</h2>
          <p class="loading-text">Please wait while we complete authentication</p>
        </div>

        <div v-else-if="error" class="error-state">
          <div class="error-icon">✕</div>
          <h2 class="error-title">Authentication Failed</h2>
          <p class="error-text">{{ error }}</p>
          <button @click="goToLogin" class="retry-button">
            Try Again
          </button>
        </div>

        <div v-else class="success-state">
          <div class="success-icon">✓</div>
          <h2 class="success-title">Successfully signed in!</h2>
          <p class="success-text">Redirecting you to the app...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isLoading = ref(true);
const error = ref<string | null>(null);

onMounted(async () => {
  try {
    // First, handle the auth callback to process URL hash fragments
    const { handleAuthCallback } = await import('@/services/auth');
    const callbackSession = await handleAuthCallback();

    // Then initialize auth store (which will pick up the session)
    await authStore.initialize();

    // Check if authenticated
    if (authStore.isAuthenticated || callbackSession) {
      // Get redirect path from query or default to dashboard
      const redirect = (route.query.redirect as string) || '/dashboard';
      
      // Small delay for better UX
      setTimeout(() => {
        router.push(redirect);
      }, 1000);
    } else {
      error.value = 'Authentication failed. Please try again.';
    }
  } catch (err: any) {
    console.error('Auth callback error:', err);
    error.value = err.message || 'An unexpected error occurred';
  } finally {
    isLoading.value = false;
  }
});

function goToLogin() {
  router.push('/');
}
</script>

<style scoped>
.auth-callback-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: var(--spacing-lg);
}

.callback-container {
  width: 100%;
  max-width: 440px;
}

.callback-card {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.loading-state,
.error-state,
.success-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border);
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-title,
.error-title,
.success-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.loading-text,
.error-text,
.success-text {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.error-icon,
.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
  color: white;
}

.error-icon {
  background: var(--color-danger);
}

.success-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.retry-button {
  padding: var(--spacing-md) var(--spacing-xl);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
}

.retry-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
</style>
