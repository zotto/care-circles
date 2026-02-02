<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="handleCancel">
        <div class="modal-container" role="dialog" aria-modal="true" aria-labelledby="diary-dialog-title">
          <div class="modal-content">
            <div v-if="icon" class="modal-icon" :class="`modal-icon--${variant}`">
              <BaseIcon :path="icon" :size="20" />
            </div>

            <h2 id="diary-dialog-title" class="modal-title">{{ title }}</h2>
            <p class="modal-message">{{ message }}</p>

            <div class="modal-field">
              <BaseTextArea
                ref="textareaRef"
                v-model="fieldValue"
                :label="fieldLabel"
                :placeholder="fieldPlaceholder"
                :max-length="maxLength"
                :show-char-count="!!maxLength"
                :rows="TEXTAREA_ROWS"
                :disabled="isLoading"
                class="modal-textarea"
              />
              <p v-if="fieldError" class="modal-field-error">{{ fieldError }}</p>
            </div>

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
import { ref, watch, computed } from 'vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import BaseTextArea from '@/components/atoms/BaseTextArea.vue';
import { mdiClose, mdiCheck } from '@mdi/js';

const TEXTAREA_ROWS = 4;

interface Props {
  title: string;
  message: string;
  fieldLabel: string;
  fieldPlaceholder: string;
  confirmText: string;
  cancelText?: string;
  loadingText?: string;
  variant?: 'primary' | 'danger' | 'warning';
  icon?: string;
  confirmIcon?: string;
  cancelIcon?: string;
  maxLength: number;
}

const props = withDefaults(defineProps<Props>(), {
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
  confirm: [value: string];
  cancel: [];
}>();

const isOpen = ref(false);
const isLoading = ref(false);
const fieldValue = ref('');
const fieldError = ref('');
const textareaRef = ref<InstanceType<typeof BaseTextArea> | null>(null);

watch(isOpen, (open) => {
  if (open) {
    fieldValue.value = '';
    fieldError.value = '';
  }
});

function open() {
  isOpen.value = true;
  isLoading.value = false;
  fieldValue.value = '';
  fieldError.value = '';
}

function close() {
  if (!isLoading.value) {
    isOpen.value = false;
  }
}

function validate(): boolean {
  const trimmed = fieldValue.value.trim();
  if (!trimmed) {
    fieldError.value = 'This field is required.';
    return false;
  }
  if (props.maxLength && trimmed.length > props.maxLength) {
    fieldError.value = `Maximum ${props.maxLength} characters.`;
    return false;
  }
  fieldError.value = '';
  return true;
}

function handleConfirm() {
  if (isLoading.value) return;
  if (!validate()) return;
  emit('confirm', fieldValue.value.trim());
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
  max-width: 420px;
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
  align-items: stretch;
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
  margin: 0 auto;
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
  text-align: left;
}

.modal-field {
  margin: var(--spacing-md) 0;
  text-align: left;
}

.modal-textarea {
  width: 100%;
}

.modal-field-error {
  font-size: var(--font-size-sm);
  color: var(--color-danger);
  margin: var(--spacing-xs) 0 0;
}

.modal-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
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
</style>
