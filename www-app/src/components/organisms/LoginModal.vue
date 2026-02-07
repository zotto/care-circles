<template>
  <Transition name="modal">
    <div v-if="modelValue" class="login-modal" @click.self="close">
      <div class="login-modal__backdrop" @click="close"></div>
      <div class="login-modal__container">
        <div class="login-modal__content">
          <button class="login-modal__close" @click="close" aria-label="Close">
            <BaseIcon :path="mdiClose" :size="20" />
          </button>

          <header class="login-modal__header">
            <img :src="logoUrl" alt="Care Circles" class="login-modal__logo" />
            <h1 class="login-modal__title">Care Circles</h1>
            <p class="login-modal__subtitle">
              {{ emailSent ? 'Check your email' : 'Sign in to coordinate care' }}
            </p>
          </header>

          <div v-if="!emailSent" class="login-modal__body">
            <form @submit.prevent="handleSubmit" class="login-form">
              <label for="email" class="sr-only">Email</label>
              <input
                id="email"
                v-model="email"
                type="email"
                class="login-form__input"
                placeholder="you@example.com"
                required
                :disabled="authStore.isLoading"
                autofocus
              />
              <BaseButton
                type="submit"
                variant="primary"
                size="md"
                icon
                :disabled="authStore.isLoading || !email || authStore.isRateLimited"
                :loading="authStore.isLoading"
                full-width
                class="login-form__submit"
              >
                <template #icon>
                  <BaseIcon :path="mdiSend" :size="18" />
                </template>
                <span v-if="cooldownSeconds > 0">Wait {{ cooldownSeconds }}s</span>
                <span v-else>Send link</span>
              </BaseButton>
              <p v-if="error" class="login-form__error">{{ error }}</p>
            </form>
          </div>

          <div v-else class="login-modal__body login-modal__success">
            <p class="success-message">
              We sent a sign-in link to <strong>{{ email }}</strong>. Click it to continue—you can close this window.
            </p>
            <button type="button" class="login-modal__link" @click="emailSent = false">
              Use a different email
            </button>
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
import logoUrl from '@/assets/logo.png';
import { mdiClose, mdiSend } from '@mdi/js';

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
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
}

.login-modal__container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 380px;
}

.login-modal__content {
  background: var(--color-bg-primary, #fff);
  border-radius: 16px;
  padding: 32px 28px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.12);
  position: relative;
}

.login-modal__close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.15s, background 0.15s;
  z-index: 1;
}

.login-modal__close:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.login-modal__header {
  text-align: center;
  margin-bottom: 28px;
}

.login-modal__logo {
  width: 56px;
  height: 56px;
  margin: 0 auto 12px;
  display: block;
  object-fit: contain;
}

.login-modal__title {
  font-size: 1.375rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 4px;
  letter-spacing: -0.02em;
}

.login-modal__subtitle {
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  margin: 0;
  font-weight: 500;
}

.login-modal__body {
  min-height: 120px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.login-form__input {
  padding: 12px 14px;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  font-size: 1rem;
  transition: border-color 0.15s, box-shadow 0.15s;
  font-family: inherit;
  height: 48px;
}

.login-form__input::placeholder {
  color: var(--color-text-tertiary);
}

.login-form__input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

.login-form__input:disabled {
  background: var(--color-bg-secondary);
  cursor: not-allowed;
}

.login-form__submit {
  margin-top: 4px;
}

.login-form__error {
  color: var(--color-danger);
  font-size: 0.875rem;
  margin: 0;
  text-align: center;
}

.login-modal__success {
  text-align: center;
  padding: 8px 0 0;
}

.login-modal__success .success-message {
  font-size: 0.9375rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0 0 20px;
}

.login-modal__link {
  background: none;
  border: none;
  font-size: 0.875rem;
  color: var(--color-primary);
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
  font-family: inherit;
}

.login-modal__link:hover {
  color: var(--color-primary-hover, var(--color-primary));
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Modal transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .login-modal__container,
.modal-leave-active .login-modal__container {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .login-modal__container,
.modal-leave-to .login-modal__container {
  opacity: 0;
  transform: scale(0.97) translateY(8px);
}

.modal-enter-to .login-modal__container,
.modal-leave-from .login-modal__container {
  opacity: 1;
  transform: scale(1) translateY(0);
}
</style>