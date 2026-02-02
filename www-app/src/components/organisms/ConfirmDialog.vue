<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="handleCancel">
        <div class="modal-container" role="dialog" aria-modal="true">
          <div class="modal-content">
            <!-- Icon -->
            <div v-if="icon" class="modal-icon" :class="`modal-icon--${variant}`">
              <BaseIcon :path="icon" :size="20" />
            </div>

            <!-- Title -->
            <h2 class="modal-title">{{ title }}</h2>

            <!-- Message -->
            <p class="modal-message">{{ message }}</p>

            <!-- Actions -->
            <div class="modal-actions" :class="{ 'modal-actions--single': !cancelText }">
              <BaseButton
                v-if="cancelText"
                variant="outline"
                size="md"
                icon
                @click="handleCancel"
                :disabled="isLoading"
              >
                <template #icon>
                  <BaseIcon :path="effectiveCancelIcon" :size="18" />
                </template>
                {{ cancelText }}
              </BaseButton>
              <BaseButton
                :variant="variant === 'danger' ? 'danger' : 'primary'"
                size="md"
                icon
                :loading="isLoading"
                @click="handleConfirm"
                :disabled="isLoading"
                class="modal-actions__confirm"
              >
                <template #icon>
                  <BaseIcon :path="effectiveConfirmIcon" :size="18" />
                </template>
                {{ confirmText }}
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import { mdiClose, mdiCheck } from '@mdi/js';

interface Props {
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  loadingText?: string;
  variant?: 'primary' | 'danger' | 'warning';
  icon?: string;
  confirmIcon?: string;
  cancelIcon?: string;
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirm Action',
  message: 'Are you sure you want to proceed?',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  loadingText: 'Processing...',
  variant: 'primary',
  icon: undefined,
  confirmIcon: undefined,
  cancelIcon: undefined,
});

const effectiveCancelIcon = computed(() => props.cancelIcon ?? mdiClose);
const effectiveConfirmIcon = computed(() => props.confirmIcon ?? mdiCheck);

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();

const isOpen = ref(false);
const isLoading = ref(false);

function open() {
  isOpen.value = true;
  isLoading.value = false;
}

function close() {
  if (!isLoading.value) {
    isOpen.value = false;
  }
}

function handleConfirm() {
  if (!isLoading.value) {
    emit('confirm');
  }
}

function handleCancel() {
  if (!isLoading.value) {
    emit('cancel');
    close();
  }
}

function setLoading(loading: boolean) {
  isLoading.value = loading;
}

// Expose methods for parent component
defineExpose({
  open,
  close,
  setLoading,
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: var(--spacing-md);
}

.modal-container {
  background: white;
  border-radius: var(--radius-md);
  box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.1), 0 6px 8px -5px rgba(0, 0, 0, 0.04);
  max-width: 360px;
  width: 100%;
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-content {
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--spacing-sm);
}

.modal-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-icon--primary {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
}

.modal-icon--danger {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.modal-icon--warning {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.modal-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.modal-message {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
  white-space: pre-line;
}

.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
  width: 100%;
  justify-content: center;
}

.modal-actions > * {
  min-width: 100px;
}

.modal-actions--single {
  justify-content: stretch;
}

.modal-actions--single .modal-actions__confirm {
  flex: 1;
  max-width: 160px;
  margin: 0 auto;
}

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

/* Responsive */
@media (max-width: 480px) {
  .modal-overlay {
    padding: var(--spacing-sm);
  }

  .modal-content {
    padding: var(--spacing-md);
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
