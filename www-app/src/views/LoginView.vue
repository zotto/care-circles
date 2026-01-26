<template>
  <div class="login-view">
    <div class="login-container">
      <div class="login-card">
        <div class="login-header">
          <h1 class="login-title">Care Circles</h1>
          <p class="login-subtitle">Sign in to coordinate care</p>
        </div>

        <div v-if="!emailSent" class="login-form">
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label for="email" class="form-label">Email address</label>
              <input
                id="email"
                v-model="email"
                type="email"
                class="form-input"
                placeholder="you@example.com"
                required
                :disabled="isLoading"
              />
            </div>

            <button
              type="submit"
              class="submit-button"
              :disabled="authStore.isLoading || !email || authStore.isRateLimited"
            >
              <span v-if="authStore.isRateLimited && authStore.rateLimitRemainingSeconds > 0">
                Wait {{ authStore.rateLimitRemainingSeconds }}s
              </span>
              <span v-else-if="!authStore.isLoading">Send Magic Link</span>
              <span v-else>Sending...</span>
            </button>

            <p v-if="error" class="error-message">{{ error }}</p>
            <p v-if="authStore.isRateLimited && !error" class="error-message">
              Rate limit active. Please wait {{ authStore.rateLimitRemainingSeconds }} second{{ authStore.rateLimitRemainingSeconds !== 1 ? 's' : '' }}.
            </p>
          </form>

          <p class="info-text">
            We'll send you a magic link for passwordless sign-in
          </p>
        </div>

        <div v-else class="success-message-container">
          <div class="success-icon">✓</div>
          <h2 class="success-title">Check your email!</h2>
          <p class="success-text">
            We've sent a magic link to <strong>{{ email }}</strong>
          </p>
          <p class="success-subtext">
            Click the link in the email to sign in. You can close this window.
          </p>
          <button @click="emailSent = false" class="back-button">
            Send to different email
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();

const email = ref('');
const emailSent = ref(false);
const error = ref<string | null>(null);
const lastRequestTime = ref<number | null>(null);
const DEBOUNCE_MS = 5000; // 5 seconds between requests

async function handleSubmit() {
  if (!email.value) return;

  // Check if we're rate limited
  if (authStore.isRateLimited) {
    error.value = `Too many requests. Please wait ${authStore.rateLimitRemainingSeconds} second${authStore.rateLimitRemainingSeconds !== 1 ? 's' : ''} before trying again.`;
    return;
  }

  // Debounce: prevent multiple rapid requests
  const now = Date.now();
  if (lastRequestTime.value && (now - lastRequestTime.value) < DEBOUNCE_MS) {
    error.value = 'Please wait a few seconds before requesting another magic link.';
    return;
  }

  error.value = null;
  lastRequestTime.value = now;

  try {
    await authStore.signInWithMagicLink(email.value);
    emailSent.value = true;
    error.value = null;
  } catch (err: any) {
    // Error is already set in authStore, but we can use it here too
    error.value = authStore.error || err.message || 'Failed to send magic link. Please try again.';
  }
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: var(--spacing-lg);
}

.login-container {
  width: 100%;
  max-width: 440px;
}

.login-card {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.login-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
}

.login-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.form-input {
  padding: var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  transition: all var(--transition-base);
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  background: var(--color-bg-secondary);
  cursor: not-allowed;
}

.submit-button {
  padding: var(--spacing-md) var(--spacing-lg);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin: 0;
  text-align: center;
}

.info-text {
  text-align: center;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.success-message-container {
  text-align: center;
}

.success-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
}

.success-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md);
}

.success-text {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-sm);
}

.success-subtext {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin: 0 0 var(--spacing-xl);
}

.back-button {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: transparent;
  color: #667eea;
  border: 1px solid #667eea;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
}

.back-button:hover {
  background: #667eea;
  color: white;
}
</style>
