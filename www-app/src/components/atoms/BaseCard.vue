<template>
  <div :class="cardClasses">
    <div v-if="$slots.header || title" class="card__header">
      <slot name="header">
        <h3 v-if="title" class="card__title">{{ title }}</h3>
      </slot>
    </div>
    
    <div class="card__body">
      <slot></slot>
    </div>
    
    <div v-if="$slots.footer" class="card__footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  title?: string;
  variant?: 'default' | 'outlined' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  hoverable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  padding: 'md',
  hoverable: false,
});

const cardClasses = computed(() => [
  'card',
  `card--${props.variant}`,
  `card--padding-${props.padding}`,
  {
    'card--hoverable': props.hoverable,
  },
]);
</script>

<style scoped>
.card {
  background-color: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

/* Variants */
.card--default {
  border: 1px solid var(--color-border);
}

.card--outlined {
  border: 2px solid var(--color-border);
}

.card--elevated {
  box-shadow: var(--shadow-md);
  border: none;
}

/* Padding */
.card--padding-none .card__body {
  padding: 0;
}

.card--padding-sm .card__body {
  padding: var(--spacing-md);
}

.card--padding-md .card__body {
  padding: var(--spacing-lg);
}

.card--padding-lg .card__body {
  padding: var(--spacing-xl);
}

/* Hoverable */
.card--hoverable {
  cursor: pointer;
}

.card--hoverable:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* Header */
.card__header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.card__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

/* Footer */
.card__footer {
  padding: var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
  background-color: var(--color-bg-secondary);
  border-bottom-left-radius: var(--radius-lg);
  border-bottom-right-radius: var(--radius-lg);
}
</style>
