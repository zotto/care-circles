<template>
  <div :class="skeletonClasses" :style="skeletonStyle">
    <span class="sr-only">Loading...</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'circular' | 'rectangular';
  animated?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'text',
  animated: true,
});

const skeletonClasses = computed(() => [
  'skeleton',
  `skeleton--${props.variant}`,
  {
    'skeleton--animated': props.animated,
  },
]);

const skeletonStyle = computed(() => {
  const style: Record<string, string> = {};
  
  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width;
  }
  
  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height;
  }
  
  return style;
});
</script>

<style scoped>
.skeleton {
  display: block;
  background: linear-gradient(
    90deg,
    var(--color-bg-tertiary) 0%,
    var(--color-border-light) 50%,
    var(--color-bg-tertiary) 100%
  );
  background-size: 200% 100%;
  border-radius: var(--radius-md);
}

.skeleton--animated {
  animation: shimmer 1.5s ease-in-out infinite;
}

.skeleton--text {
  height: 1em;
  margin-bottom: var(--spacing-xs);
  border-radius: var(--radius-sm);
}

.skeleton--circular {
  border-radius: 50%;
  width: 40px;
  height: 40px;
}

.skeleton--rectangular {
  width: 100%;
  height: 100px;
}

@keyframes shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}
</style>
