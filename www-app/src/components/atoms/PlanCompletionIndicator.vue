<template>
  <div class="plan-completion" role="status" :aria-label="ariaLabel">
    <template v-if="loading">
      <span class="plan-completion__skeleton" aria-hidden="true">—</span>
    </template>
    <template v-else>
      <div class="plan-completion__bar-wrap">
        <div
          class="plan-completion__bar"
          :class="{ 'plan-completion__bar--empty': total === 0 }"
          :style="{ '--progress': progressPercent }"
        />
      </div>
      <span class="plan-completion__label">
        {{ completionLabel }}
      </span>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  /** Total number of tasks in the plan */
  total: number;
  /** Number of tasks with status completed */
  completed: number;
  /** Whether task counts are still loading */
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
});

const progressPercent = computed(() => {
  if (props.total <= 0) return 0;
  return Math.min(100, Math.round((props.completed / props.total) * 100));
});

const completionLabel = computed(() => {
  if (props.total === 0) return '0 tasks';
  return `${props.completed} of ${props.total} tasks completed`;
});

const ariaLabel = computed(() => {
  if (props.loading) return 'Loading task progress';
  if (props.total === 0) return 'No tasks in this plan';
  return `Plan progress: ${props.completed} of ${props.total} tasks completed`;
});
</script>

<style scoped>
.plan-completion {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.plan-completion__skeleton {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

.plan-completion__bar-wrap {
  flex: 1;
  min-width: 80px;
  max-width: 140px;
  height: 8px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.plan-completion__bar {
  height: 100%;
  width: calc(var(--progress, 0) * 1%);
  background: var(--color-success);
  border-radius: var(--radius-full);
  transition: width 0.25s ease;
}

.plan-completion__bar--empty {
  width: 0;
}

.plan-completion__label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  white-space: nowrap;
}
</style>
