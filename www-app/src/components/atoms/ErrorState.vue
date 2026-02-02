<template>
  <div class="error-state" :class="{ 'error-state--compact': compact }">
    <div v-if="icon || $slots.icon" class="error-state__icon">
      <slot name="icon">
        <BaseIcon v-if="icon" :path="icon" :size="iconSize" />
      </slot>
    </div>
    <h3 v-if="title" class="error-state__title">{{ title }}</h3>
    <p v-if="message || $slots.message" class="error-state__message">
      <slot name="message">{{ message }}</slot>
    </p>
    <div v-if="$slots.action" class="error-state__action">
      <slot name="action"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseIcon from './BaseIcon.vue';

interface Props {
  icon?: string;
  iconSize?: number;
  title?: string;
  message?: string;
  compact?: boolean;
}

withDefaults(defineProps<Props>(), {
  iconSize: 48,
  title: 'Something went wrong',
  compact: false,
});
</script>

<style scoped>
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
  min-height: 300px;
}

.error-state--compact {
  padding: var(--spacing-2xl) var(--spacing-lg);
  min-height: 200px;
}

.error-state__icon {
  color: var(--color-error);
  margin-bottom: var(--spacing-lg);
  opacity: 0.9;
}

.error-state__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md);
}

.error-state--compact .error-state__title {
  font-size: var(--font-size-lg);
}

.error-state__message {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  max-width: 500px;
  margin: 0 auto var(--spacing-xl);
}

.error-state--compact .error-state__message {
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-lg);
}

.error-state__action {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
  justify-content: center;
}
</style>
