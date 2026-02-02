<template>
  <div class="loading-state" :class="{ 'loading-state--compact': compact }">
    <LoadingSpinner :size="spinnerSize" :variant="variant" />
    <p v-if="text" class="loading-state__text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
import LoadingSpinner from './LoadingSpinner.vue';

interface Props {
  text?: string;
  compact?: boolean;
  spinnerSize?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'secondary' | 'white';
}

withDefaults(defineProps<Props>(), {
  text: 'Loading...',
  compact: false,
  spinnerSize: 'lg',
  variant: 'primary',
});
</script>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
  min-height: 300px;
  gap: var(--spacing-lg);
}

.loading-state--compact {
  padding: var(--spacing-2xl) var(--spacing-lg);
  min-height: 200px;
}

.loading-state__text {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
  font-weight: var(--font-weight-medium);
}

.loading-state--compact .loading-state__text {
  font-size: var(--font-size-sm);
}
</style>
