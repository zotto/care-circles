<template>
  <Transition name="modal">
    <div v-if="modelValue" class="login-modal" @click.self="close">
      <div class="login-modal__backdrop" @click="close"></div>
      <div class="login-modal__container">
        <div class="login-modal__content">
          <button class="login-modal__close" @click="close" aria-label="Close">
            <BaseIcon :path="mdiClose" :size="20" />
          </button>

          <div class="login-modal__header">
            <div class="login-modal__logo">
              <BaseIcon :path="mdiHeartCircle" :size="24" />
            </div>
            <h2 class="login-modal__title">Welcome to Care Circles</h2>
            <p class="login-modal__subtitle">Sign in to coordinate care</p>
          </div>

          <div v-if="!emailSent" class="login-modal__form">
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
                  autofocus
                />
              </div>

              <BaseButton
                type="submit"
                variant="primary"
                size="md"
                :disabled="authStore.isLoading || !email || authStore.isRateLimited"
                :loading="authStore.isLoading"
                full-width
                class="form-submit-button"
              >
                <span v-if="cooldownSeconds > 0">
                  Wait {{ cooldownSeconds }}s
                </span>
                <span v-else>
                  Send Magic Link
                </span>
              </BaseButton>

              <p v-if="error" class="error-message">{{ error }}</p>
              <p v-if="cooldownSeconds > 0 && !error" class="error-message">
                Rate limit active. Please wait {{ cooldownSeconds }} second{{ cooldownSeconds !== 1 ? 's' : '' }}.
              </p>
            </form>

            <p class="info-text">
              We'll send you a magic link for passwordless sign-in
            </p>
          </div>

          <div v-else class="login-modal__success">
            <div class="success-icon">✓</div>
            <h3 class="success-title">Check your email!</h3>
            <p class="success-text">
              We've sent a magic link to <strong>{{ email }}</strong>
            </p>
            <p class="success-subtext">
              Click the link in the email to sign in. You can close this window.
            </p>
            <BaseButton
              variant="outline"
              size="md"
              @click="emailSent = false"
            >
              Send to different email
            </BaseButton>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import { mdiHeartCircle, mdiClose } from '@mdi/js';

interface Props {
  modelValue: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update:modelValue': [value: boolean];
}>();

const authStore = useAuthStore();

const email = ref('');
const emailSent = ref(false);
const error = ref<string | null>(null);
const lastRequestTime = ref<number | null>(null);
const cooldownSeconds = ref<number>(0);
const DEBOUNCE_MS = 5000; // 5 seconds between requests

// Watch rate limit state from authStore
watch(() => authStore.rateLimitRemainingSeconds, (seconds) => {
  cooldownSeconds.value = seconds;
}, { immediate: true });

// Update cooldown display every second
let cooldownInterval: ReturnType<typeof setInterval> | null = null;

watch(() => authStore.isRateLimited, (isLimited) => {
  if (isLimited && !cooldownInterval) {
    cooldownInterval = setInterval(() => {
      cooldownSeconds.value = authStore.rateLimitRemainingSeconds;
      if (cooldownSeconds.value <= 0 && cooldownInterval) {
        clearInterval(cooldownInterval);
        cooldownInterval = null;
      }
    }, 1000);
  } else if (!isLimited && cooldownInterval) {
    clearInterval(cooldownInterval);
    cooldownInterval = null;
    cooldownSeconds.value = 0;
  }
}, { immediate: true });

onUnmounted(() => {
  if (cooldownInterval) {
    clearInterval(cooldownInterval);
    cooldownInterval = null;
  }
});

const close = () => {
  emit('update:modelValue', false);
  // Reset form when closing (but keep rate limit state)
  setTimeout(() => {
    email.value = '';
    emailSent.value = false;
    error.value = null;
  }, 300);
};

// Close on escape key
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        close();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }
});

async function handleSubmit() {
  if (!email.value) return;

  // Check if we're rate limited (authStore handles this, but show error here too)
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
.login-modal {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}

.login-modal__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.login-modal__container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  max-height: 90vh;
  overflow-y: auto;
}

.login-modal__content {
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-2xl);
  position: relative;
}

.login-modal__close {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-secondary);
  border: none;
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
  z-index: 1;
}

.login-modal__close:hover {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.login-modal__header {
  text-align: center;
  margin-bottom: var(--spacing-lg);
}

.login-modal__logo {
  width: 48px;
  height: 48px;
  margin: 0 auto var(--spacing-sm);
  background: var(--color-primary-subtle);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
}

.login-modal__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.login-modal__subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.login-modal__form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input {
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  transition: all var(--transition-base);
  font-family: var(--font-family-base);
  height: 44px;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.form-input:disabled {
  background: var(--color-bg-secondary);
  cursor: not-allowed;
}

.form-submit-button {
  margin-top: var(--spacing-md);
}

.error-message {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin: 0;
  text-align: center;
}

.info-text {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin: 0;
  line-height: 1.4;
}

.login-modal__success {
  text-align: center;
  padding: var(--spacing-md) 0;
}

.success-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  background: var(--color-primary-gradient);
  color: white;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
}

.success-title {
  font-size: var(--font-size-xl);
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

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity var(--transition-base);
}

.modal-enter-active .login-modal__container,
.modal-leave-active .login-modal__container {
  transition: transform var(--transition-base), opacity var(--transition-base);
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .login-modal__container,
.modal-leave-to .login-modal__container {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

.modal-enter-to .login-modal__container,
.modal-leave-from .login-modal__container {
  opacity: 1;
  transform: scale(1) translateY(0);
}
</style>