<template>
  <div class="empty-state" :class="{ 'empty-state--compact': compact }">
    <div v-if="icon || $slots.icon" class="empty-state__icon">
      <slot name="icon">
        <BaseIcon v-if="icon" :path="icon" :size="iconSize" />
      </slot>
    </div>
    <h3 v-if="title" class="empty-state__title">{{ title }}</h3>
    <p v-if="description || $slots.description" class="empty-state__description">
      <slot name="description">{{ description }}</slot>
    </p>
    <div v-if="$slots.action" class="empty-state__action">
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
  description?: string;
  compact?: boolean;
}

withDefaults(defineProps<Props>(), {
  iconSize: 48,
  compact: false,
});
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
  min-height: 300px;
}

.empty-state--compact {
  padding: var(--spacing-2xl) var(--spacing-lg);
  min-height: 200px;
}

.empty-state__icon {
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-lg);
  opacity: 0.6;
}

.empty-state__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md);
}

.empty-state--compact .empty-state__title {
  font-size: var(--font-size-lg);
}

.empty-state__description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  max-width: 500px;
  margin: 0 auto var(--spacing-xl);
}

.empty-state--compact .empty-state__description {
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-lg);
}

.empty-state__action {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
  justify-content: center;
}
</style>
