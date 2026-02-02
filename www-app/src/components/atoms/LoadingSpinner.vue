<template>
  <div class="loading-spinner" :class="[`loading-spinner--${size}`, `loading-spinner--${variant}`]">
    <div class="loading-spinner__circle"></div>
    <span v-if="text" class="loading-spinner__text">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'white';
  text?: string;
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  variant: 'primary',
});
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
}

.loading-spinner__circle {
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  /* Keep spin animation running on mobile (GPU layer) */
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
}

/* Sizes */
.loading-spinner--sm .loading-spinner__circle {
  width: 20px;
  height: 20px;
  border-width: 2px;
}

.loading-spinner--md .loading-spinner__circle {
  width: 32px;
  height: 32px;
  border-width: 3px;
}

.loading-spinner--lg .loading-spinner__circle {
  width: 48px;
  height: 48px;
  border-width: 4px;
}

.loading-spinner--xl .loading-spinner__circle {
  width: 64px;
  height: 64px;
  border-width: 4px;
}

/* Variants */
.loading-spinner--primary .loading-spinner__circle {
  border: currentColor solid;
  border-right-color: transparent;
  color: var(--color-primary);
}

.loading-spinner--secondary .loading-spinner__circle {
  border: currentColor solid;
  border-right-color: transparent;
  color: var(--color-secondary);
}

.loading-spinner--white .loading-spinner__circle {
  border: currentColor solid;
  border-right-color: transparent;
  color: white;
}

.loading-spinner__text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

@keyframes spin {
  to {
    transform: translateZ(0) rotate(360deg);
  }
}
</style>
