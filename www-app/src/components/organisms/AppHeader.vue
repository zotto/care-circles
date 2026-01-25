<template>
  <header class="app-header">
    <div class="container">
      <div class="app-header__content">
        <div class="app-header__brand">
          <div class="app-header__logo">
            <BaseIcon :path="mdiHeartCircle" :size="32" />
          </div>
          <div class="app-header__title">
            <h1 class="app-header__name">Care Circles</h1>
            <p class="app-header__tagline">Together in care</p>
          </div>
        </div>
        
        <nav class="app-header__nav" v-if="showNav">
          <slot name="nav"></slot>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import { mdiHeartCircle } from '@mdi/js';

interface Props {
  showNav?: boolean;
}

withDefaults(defineProps<Props>(), {
  showNav: false,
});
</script>

<style scoped>
.app-header {
  background-color: rgba(255, 255, 255, 0.95);
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  transition: all var(--transition-base);
}

.app-header__content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) 0;
}

.app-header__brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  cursor: pointer;
  transition: opacity var(--transition-base);
}

.app-header__brand:hover {
  opacity: 0.8;
}

.app-header__logo {
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, #fdf2f8 100%);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

.app-header__logo svg {
  transition: transform var(--transition-base);
}

.app-header__brand:hover .app-header__logo {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, #fce7f3 100%);
}

.app-header__title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.app-header__name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1;
}

.app-header__tagline {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1;
  font-weight: var(--font-weight-medium);
}

.app-header__nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

@media (max-width: 640px) {
  .app-header__content {
    padding: var(--spacing-md) 0;
  }

  .app-header__tagline {
    display: none;
  }
  
  .app-header__name {
    font-size: var(--font-size-base);
  }
  
  .app-header__logo {
    width: 36px;
    height: 36px;
  }
  
  .app-header__logo svg {
    width: 20px;
    height: 20px;
  }
}
</style>
