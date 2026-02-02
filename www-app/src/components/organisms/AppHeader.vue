<template>
  <header class="app-header">
    <div class="app-header__container">
      <!-- Left: Brand -->
      <router-link :to="isAuthenticated ? '/my-plans' : '/'" class="app-header__brand">
        <div class="app-header__logo">
          <BaseIcon :path="mdiHeartCircle" :size="20" />
        </div>
        <span class="app-header__name">Care Circles</span>
      </router-link>
      
      <!-- Center: Navigation (only when authenticated) -->
      <nav v-if="isAuthenticated" class="app-header__nav">
        <router-link 
          to="/my-plans" 
          class="app-header__nav-link"
          :class="{ 'is-active': currentRoute === '/my-plans' }"
        >
          <BaseIcon :path="mdiFileDocumentMultiple" :size="16" />
          <span>My Plans</span>
        </router-link>
        <router-link 
          to="/my-tasks" 
          class="app-header__nav-link"
          :class="{ 'is-active': currentRoute === '/my-tasks' }"
        >
          <BaseIcon :path="mdiClipboardCheck" :size="16" />
          <span>My Tasks</span>
        </router-link>
      </nav>

      <!-- Right: User Menu or Sign In -->
      <div class="app-header__user">
        <!-- Authenticated: User Menu -->
        <template v-if="isAuthenticated && user">
          <div class="app-header__user-wrapper">
            <button class="app-header__user-trigger" @click="toggleUserMenu" ref="userMenuTrigger">
              <div class="app-header__user-avatar">
                <BaseIcon :path="mdiAccount" :size="18" />
              </div>
              <span class="app-header__username">{{ displayName }}</span>
              <BaseIcon 
                :path="mdiChevronDown" 
                :size="16" 
                class="app-header__dropdown-icon"
                :class="{ 'is-open': isUserMenuOpen }"
              />
            </button>

            <!-- Dropdown Menu -->
            <Transition name="dropdown">
              <div 
                v-if="isUserMenuOpen" 
                class="app-header__dropdown"
                ref="userMenuDropdown"
              >
                <div class="app-header__dropdown-section">
                  <button class="app-header__dropdown-item" @click="navigateTo('/my-plans')">
                    <BaseIcon :path="mdiFileDocumentMultiple" :size="18" />
                    <span>My Plans</span>
                  </button>
                  <button class="app-header__dropdown-item" @click="navigateTo('/my-tasks')">
                    <BaseIcon :path="mdiClipboardCheck" :size="18" />
                    <span>My Tasks</span>
                  </button>
                </div>

                <div class="app-header__dropdown-divider"></div>

                <div class="app-header__dropdown-section">
                  <button class="app-header__dropdown-item app-header__dropdown-item--danger" @click="handleSignOut">
                    <BaseIcon :path="mdiLogout" :size="18" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            </Transition>
          </div>
        </template>

        <!-- Not Authenticated: Sign In Button -->
        <template v-else>
          <button class="app-header__sign-in" @click="openLoginModal">
            <BaseIcon :path="mdiLogin" :size="18" />
            <span>Sign In</span>
          </button>
        </template>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useLoginModal } from '@/composables/useLoginModal';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import { 
  mdiHeartCircle, 
  mdiFileDocumentMultiple,
  mdiClipboardCheck,
  mdiAccount,
  mdiChevronDown,
  mdiLogout,
  mdiLogin
} from '@mdi/js';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { open: openLoginModal } = useLoginModal();

const user = computed(() => authStore.user);
const isAuthenticated = computed(() => authStore.isAuthenticated);

const displayName = computed(() => {
  if (!user.value) return 'User';
  return user.value.user_metadata?.full_name || 
         user.value.email?.split('@')[0] || 
         'User';
});

const isUserMenuOpen = ref(false);
const userMenuTrigger = ref<HTMLElement | null>(null);
const userMenuDropdown = ref<HTMLElement | null>(null);

const currentRoute = computed(() => route.path);

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value;
};

const closeUserMenu = () => {
  isUserMenuOpen.value = false;
};

const navigateTo = (path: string) => {
  router.push(path);
  closeUserMenu();
};

const handleSignOut = async () => {
  try {
    await authStore.signOut();
    closeUserMenu();
    router.push('/');
  } catch (error) {
    console.error('Error signing out:', error);
  }
};

// Close dropdown when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  if (
    isUserMenuOpen.value &&
    userMenuTrigger.value &&
    userMenuDropdown.value &&
    !userMenuTrigger.value.contains(event.target as Node) &&
    !userMenuDropdown.value.contains(event.target as Node)
  ) {
    closeUserMenu();
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.app-header {
  background-color: rgba(255, 255, 255, 0.98);
  border-bottom: 1px solid var(--color-border-light);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  transition: all var(--transition-base);
  height: var(--height-header);
}

.app-header__container {
  max-width: var(--container-2xl);
  margin: 0 auto;
  padding: 0 var(--layout-padding-desktop);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--component-gap-lg);
}

@media (max-width: 1024px) {
  .app-header__container {
    padding: 0 var(--layout-padding-tablet);
  }
}

@media (max-width: 768px) {
  .app-header__container {
    padding: 0 var(--layout-padding-mobile);
    gap: var(--component-gap-md);
  }
}

/* Brand */
.app-header__brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  text-decoration: none;
  color: var(--color-text-primary);
  transition: opacity var(--transition-base);
  flex-shrink: 0;
}

.app-header__brand:hover {
  opacity: 0.7;
}

.app-header__logo {
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, #fdf2f8 100%);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

.app-header__brand:hover .app-header__logo {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, #fce7f3 100%);
  transform: scale(1.05);
}

.app-header__name {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Navigation */
.app-header__nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex: 1;
  justify-content: center;
}

@media (max-width: 768px) {
  .app-header__nav {
    display: none;
  }
}

.app-header__nav-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-button);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all var(--transition-base);
  position: relative;
}

.app-header__nav-link:hover {
  color: var(--color-primary);
  background-color: var(--color-bg-secondary);
}

.app-header__nav-link.is-active {
  color: var(--color-primary);
  background-color: var(--color-primary-subtle);
  font-weight: var(--font-weight-semibold);
}

.app-header__nav-link.is-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: var(--spacing-md);
  right: var(--spacing-md);
  height: 2px;
  background: var(--color-primary);
  border-radius: var(--radius-full);
}

/* User Menu */
.app-header__user {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-shrink: 0;
}

.app-header__user-wrapper {
  position: relative;
}

.app-header__user-trigger {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-button);
  cursor: pointer;
  transition: all var(--transition-base);
  border: 1px solid transparent;
  background: none;
  font-family: var(--font-family-base);
}

.app-header__user-trigger:hover {
  background-color: var(--color-bg-secondary);
  border-color: var(--color-border);
}

.app-header__user-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--color-primary-gradient);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.app-header__username {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .app-header__username {
    display: none;
  }
}

.app-header__dropdown-icon {
  color: var(--color-text-tertiary);
  transition: transform var(--transition-base);
  flex-shrink: 0;
}

.app-header__dropdown-icon.is-open {
  transform: rotate(180deg);
}

/* Dropdown */
.app-header__dropdown {
  position: absolute;
  top: calc(100% + var(--spacing-sm));
  right: 0;
  min-width: 200px;
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-dropdown);
  border: 1px solid var(--color-border);
  overflow: hidden;
  z-index: var(--z-dropdown);
}

.app-header__dropdown-section {
  padding: var(--spacing-sm);
}

.app-header__dropdown-divider {
  height: 1px;
  background-color: var(--color-border-light);
  margin: 0;
}

.app-header__dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  width: 100%;
  padding: var(--spacing-md) var(--spacing-lg);
  border: none;
  background: none;
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  text-align: left;
  transition: all var(--transition-fast);
  font-family: var(--font-family-base);
  border-radius: var(--radius-md);
}

.app-header__dropdown-item:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-primary);
}

.app-header__dropdown-item--danger {
  color: var(--color-error);
}

.app-header__dropdown-item--danger:hover {
  background-color: var(--color-error-light);
  color: var(--color-error);
}

/* Sign In Button */
.app-header__sign-in {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-xl);
  border-radius: var(--radius-button);
  background: var(--color-primary);
  color: white;
  border: none;
  cursor: pointer;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  transition: all var(--transition-base);
  font-family: var(--font-family-base);
  box-shadow: var(--shadow-button);
}

.app-header__sign-in:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-button-hover);
}

.app-header__sign-in:active {
  transform: translateY(0);
}

/* Dropdown Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity var(--transition-fast), transform var(--transition-fast);
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
