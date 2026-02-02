<template>
  <div class="empty-card">
    <div class="empty-card__decoration">
      <div class="empty-card__circle empty-card__circle--1"></div>
      <div class="empty-card__circle empty-card__circle--2"></div>
    </div>
    <div class="empty-card__content">
      <div class="empty-card__icon">
        <slot name="icon">
          <BaseIcon v-if="icon" :path="icon" :size="64" />
        </slot>
      </div>
      <h3 class="empty-card__title">{{ title }}</h3>
      <p class="empty-card__description">{{ description }}</p>
      <div v-if="$slots.action" class="empty-card__action">
        <slot name="action"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseIcon from './BaseIcon.vue';

interface Props {
  icon?: string;
  title: string;
  description: string;
}

defineProps<Props>();
</script>

<style scoped>
.empty-card {
  position: relative;
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-secondary) 100%);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--spacing-5xl) var(--spacing-3xl);
  text-align: center;
  overflow: hidden;
  box-shadow: var(--shadow-card);
  transition: all var(--transition-slow);
}

.empty-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.empty-card__decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.empty-card__circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.04;
  filter: blur(60px);
}

.empty-card__circle--1 {
  width: 300px;
  height: 300px;
  background: var(--color-primary);
  top: -150px;
  right: -100px;
  animation: float 8s ease-in-out infinite;
}

.empty-card__circle--2 {
  width: 200px;
  height: 200px;
  background: var(--color-accent);
  bottom: -80px;
  left: -60px;
  animation: float 6s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20px, -20px);
  }
}

.empty-card__content {
  position: relative;
  z-index: 1;
}

.empty-card__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  margin: 0 auto var(--spacing-xl);
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, rgba(236, 72, 153, 0.1) 100%);
  border-radius: var(--radius-2xl);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.empty-card__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg);
  letter-spacing: -0.01em;
}

.empty-card__description {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  max-width: 500px;
  margin: 0 auto var(--spacing-2xl);
}

.empty-card__action {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}
</style>
