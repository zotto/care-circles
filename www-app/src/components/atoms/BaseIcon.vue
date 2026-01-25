<template>
  <svg 
    :width="size" 
    :height="size" 
    :viewBox="viewBox"
    :class="iconClasses"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path :d="path" :fill="currentColor" />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  path: string;
  size?: number | string;
  color?: string;
  rotate?: number;
}

const props = withDefaults(defineProps<Props>(), {
  size: 24,
  color: 'currentColor',
  rotate: 0,
});

const viewBox = computed(() => '0 0 24 24');

const currentColor = computed(() => props.color);

const iconClasses = computed(() => ['mdi-icon']);

</script>

<style scoped>
.mdi-icon {
  display: inline-block;
  vertical-align: middle;
  transition: transform var(--transition-base);
}
</style>
