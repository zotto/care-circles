<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <span v-if="loading" class="button__spinner"></span>
    <span v-if="icon && !loading" class="button__icon">
      <slot name="icon"></slot>
    </span>
    <span class="button__content">
      <slot></slot>
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { ButtonVariant, ButtonSize } from '@/types';

interface Props {
  variant?: ButtonVariant;
  size?: ButtonSize;
  disabled?: boolean;
  loading?: boolean;
  icon?: boolean;
  fullWidth?: boolean;
  type?: 'button' | 'submit' | 'reset';
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  icon: false,
  fullWidth: false,
  type: 'button',
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const buttonClasses = computed(() => [
  'button',
  `button--${props.variant}`,
  `button--${props.size}`,
  {
    'button--loading': props.loading,
    'button--disabled': props.disabled,
    'button--full-width': props.fullWidth,
  },
]);

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>

<style scoped>
.button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-base);
  font-weight: var(--font-weight-medium);
  text-align: center;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
  user-select: none;
  overflow: hidden;
}

.button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, transparent 100%);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.button:hover::before {
  opacity: 1;
}

.button::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-md);
  opacity: 0;
  transition: opacity var(--transition-fast);
  pointer-events: none;
}

.button:focus-visible {
  outline: none;
}

.button:focus-visible::after {
  opacity: 1;
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
}

/* Sizes */
.button--sm {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-sm);
  height: 32px;
}

.button--md {
  padding: var(--spacing-sm) var(--spacing-lg);
  font-size: var(--font-size-base);
  height: 40px;
}

.button--lg {
  padding: var(--spacing-md) var(--spacing-xl);
  font-size: var(--font-size-lg);
  height: 48px;
  font-weight: var(--font-weight-semibold);
}

/* Variants */
.button--primary {
  background: var(--color-primary-gradient);
  color: var(--color-text-inverse);
  box-shadow: var(--shadow-sm);
}

.button--primary:hover:not(.button--disabled):not(.button--loading) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-colored);
}

.button--primary:active:not(.button--disabled):not(.button--loading) {
  transform: translateY(0);
  box-shadow: var(--shadow-sm);
}

.button--secondary {
  background: var(--color-secondary-gradient);
  color: var(--color-text-inverse);
  box-shadow: var(--shadow-sm);
}

.button--secondary:hover:not(.button--disabled):not(.button--loading) {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px -10px rgba(236, 72, 153, 0.4);
}

.button--secondary:active:not(.button--disabled):not(.button--loading) {
  transform: translateY(0);
}

.button--outline {
  background-color: transparent;
  color: var(--color-primary);
  border: 2px solid var(--color-primary);
  box-shadow: none;
}

.button--outline:hover:not(.button--disabled):not(.button--loading) {
  background-color: var(--color-primary-subtle);
  border-color: var(--color-primary-dark);
  transform: translateY(-2px);
}

.button--ghost {
  background-color: transparent;
  color: var(--color-text-primary);
}

.button--ghost:hover:not(.button--disabled):not(.button--loading) {
  background-color: var(--color-bg-tertiary);
}

.button--danger {
  background-color: var(--color-error);
  color: var(--color-text-inverse);
  box-shadow: var(--shadow-sm);
}

.button--danger:hover:not(.button--disabled):not(.button--loading) {
  background-color: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 10px 40px -10px rgba(239, 68, 68, 0.4);
}

/* States */
.button--disabled,
.button--loading {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.button--full-width {
  width: 100%;
}

/* Loading Spinner */
.button__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.button__content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  position: relative;
  z-index: 1;
}

/* Ripple Effect */
@keyframes ripple-effect {
  to {
    transform: scale(4);
    opacity: 0;
  }
}
</style>
