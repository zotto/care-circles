<template>
  <footer class="app-footer">
    <div class="container">
      <div class="app-footer__content">
        <div class="app-footer__info">
          <p class="app-footer__text">
            &copy; {{ currentYear }} Care Circles. Built with care for caregivers.
          </p>
        </div>
        <div class="app-footer__links">
          <a href="#" class="app-footer__link">Privacy</a>
          <span class="app-footer__separator">•</span>
          <a href="#" class="app-footer__link">Terms</a>
          <span class="app-footer__separator">•</span>
          <a href="#" class="app-footer__link">Support</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const currentYear = computed(() => new Date().getFullYear());
</script>

<style scoped>
.app-footer {
  background-color: var(--color-bg-primary);
  border-top: 1px solid var(--color-border);
  margin-top: auto;
  padding: var(--spacing-xl) 0;
}

.app-footer__content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
}

.app-footer__info {
  flex: 1;
}

.app-footer__text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.app-footer__links {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.app-footer__link {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.app-footer__link:hover {
  color: var(--color-primary);
}

.app-footer__separator {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

@media (max-width: 640px) {
  .app-footer__content {
    flex-direction: column;
    text-align: center;
  }
}
</style>
