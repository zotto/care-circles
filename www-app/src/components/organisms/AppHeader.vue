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
  background-color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  transition: all var(--transition-base);
}

.app-header::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-primary-light), transparent);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.app-header:hover::after {
  opacity: 0.5;
}

.app-header__content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) 0;
}

.app-header__brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  cursor: pointer;
  transition: transform var(--transition-base);
}

.app-header__brand:hover {
  transform: translateY(-2px);
}

.app-header__logo {
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, #fdf2f8 100%);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.app-header__logo::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  opacity: 0;
  transition: opacity var(--transition-base);
}

.app-header__brand:hover .app-header__logo::before {
  opacity: 0.1;
}

.app-header__logo svg {
  position: relative;
  z-index: 1;
  transition: transform var(--transition-base);
}

.app-header__brand:hover .app-header__logo svg {
  transform: scale(1.1);
}

.app-header__title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.app-header__name {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1;
  background: linear-gradient(135deg, var(--color-text-primary) 0%, var(--color-primary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.app-header__tagline {
  font-size: var(--font-size-sm);
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
  .app-header__tagline {
    display: none;
  }
  
  .app-header__name {
    font-size: var(--font-size-lg);
  }
  
  .app-header__logo {
    width: 40px;
    height: 40px;
  }
  
  .app-header__logo svg {
    width: 24px;
    height: 24px;
  }
}
</style>
