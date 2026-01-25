<template>
  <div :class="badgeClasses">
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md' | 'lg';
  outlined?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'neutral',
  size: 'md',
  outlined: false,
});

const badgeClasses = computed(() => [
  'badge',
  `badge--${props.variant}`,
  `badge--${props.size}`,
  {
    'badge--outlined': props.outlined,
  },
]);
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-full);
  white-space: nowrap;
}

/* Sizes */
.badge--sm {
  padding: var(--spacing-xs) var(--spacing-sm);
  font-size: var(--font-size-xs);
  height: 20px;
}

.badge--md {
  padding: var(--spacing-xs) var(--spacing-md);
  font-size: var(--font-size-sm);
  height: 24px;
}

.badge--lg {
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-base);
  height: 28px;
}

/* Variants - Filled */
.badge--primary {
  background-color: var(--color-primary);
  color: var(--color-text-inverse);
}

.badge--secondary {
  background-color: var(--color-secondary);
  color: var(--color-text-inverse);
}

.badge--success {
  background-color: var(--color-success);
  color: var(--color-text-inverse);
}

.badge--warning {
  background-color: var(--color-warning);
  color: var(--color-text-inverse);
}

.badge--error {
  background-color: var(--color-error);
  color: var(--color-text-inverse);
}

.badge--info {
  background-color: var(--color-info);
  color: var(--color-text-inverse);
}

.badge--neutral {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

/* Outlined Variants */
.badge--outlined.badge--primary {
  background-color: var(--color-primary-subtle);
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}

.badge--outlined.badge--secondary {
  background-color: #fdf2f8;
  color: var(--color-secondary);
  border: 1px solid var(--color-secondary);
}

.badge--outlined.badge--success {
  background-color: var(--color-success-light);
  color: var(--color-success);
  border: 1px solid var(--color-success);
}

.badge--outlined.badge--warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
  border: 1px solid var(--color-warning);
}

.badge--outlined.badge--error {
  background-color: var(--color-error-light);
  color: var(--color-error);
  border: 1px solid var(--color-error);
}

.badge--outlined.badge--info {
  background-color: var(--color-info-light);
  color: var(--color-info);
  border: 1px solid var(--color-info);
}

.badge--outlined.badge--neutral {
  background-color: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}
</style>
