<template>
  <header class="app-header">
    <div class="app-header__container">
      <!-- Left: Brand -->
      <router-link :to="isAuthenticated ? '/dashboard' : '/'" class="app-header__brand">
        <div class="app-header__logo">
          <BaseIcon :path="mdiHeartCircle" :size="20" />
        </div>
        <span class="app-header__name">Care Circles</span>
      </router-link>
      
      <!-- Center: Navigation (only when authenticated) -->
      <nav v-if="isAuthenticated" class="app-header__nav">
        <router-link 
          to="/dashboard" 
          class="app-header__nav-link"
          :class="{ 'is-active': currentRoute === '/dashboard' }"
        >
          <BaseIcon :path="mdiHome" :size="16" />
          <span>Home</span>
        </router-link>
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
          <div class="app-header__user-trigger" @click="toggleUserMenu" ref="userMenuTrigger">
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
          </div>

          <!-- Dropdown Menu -->
          <Transition name="dropdown">
            <div 
              v-if="isUserMenuOpen" 
              class="app-header__dropdown"
              ref="userMenuDropdown"
            >
              <div class="app-header__dropdown-section">
                <div class="app-header__dropdown-user-info">
                  <div class="app-header__dropdown-avatar">
                    <BaseIcon :path="mdiAccount" :size="24" />
                  </div>
                  <div class="app-header__dropdown-user-details">
                    <div class="app-header__dropdown-name">{{ displayName }}</div>
                    <div class="app-header__dropdown-email">{{ user.email }}</div>
                  </div>
                </div>
              </div>

              <div class="app-header__dropdown-divider"></div>

              <div class="app-header__dropdown-section">
                <button class="app-header__dropdown-item" @click="navigateTo('/my-plans')">
                  <BaseIcon :path="mdiFileDocumentMultiple" :size="18" />
                  <span>My Plans</span>
                </button>
                <button class="app-header__dropdown-item" @click="navigateTo('/my-tasks')">
                  <BaseIcon :path="mdiClipboardCheck" :size="18" />
                  <span>My Tasks</span>
                </button>
                <button class="app-header__dropdown-item" @click="navigateTo('/settings')">
                  <BaseIcon :path="mdiCog" :size="18" />
                  <span>Settings</span>
                </button>
                <button class="app-header__dropdown-item" @click="navigateTo('/profile')">
                  <BaseIcon :path="mdiAccountCircle" :size="18" />
                  <span>Profile</span>
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
  mdiHome, 
  mdiFileDocumentMultiple,
  mdiClipboardCheck,
  mdiAccount,
  mdiChevronDown,
  mdiCog,
  mdiAccountCircle,
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
  background-color: rgba(255, 255, 255, 0.97);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  transition: all var(--transition-base);
  height: 56px;
}

.app-header__container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-xl);
}

/* Brand */
.app-header__brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
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
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, #fdf2f8 100%);
  border-radius: var(--radius-sm);
  transition: all var(--transition-base);
}

.app-header__brand:hover .app-header__logo {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, #fce7f3 100%);
}

.app-header__name {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  line-height: 1;
  white-space: nowrap;
}

/* Navigation */
.app-header__nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  flex: 1;
  justify-content: center;
}

.app-header__nav-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-sm);
  transition: all var(--transition-base);
  white-space: nowrap;
}

.app-header__nav-link:hover {
  color: var(--color-text-primary);
  background-color: rgba(0, 0, 0, 0.04);
}

.app-header__nav-link.is-active {
  color: var(--color-primary);
  background-color: var(--color-primary-subtle);
}

/* User Menu */
.app-header__user {
  position: relative;
  flex-shrink: 0;
}

.app-header__user-trigger {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: transparent;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-base);
}

.app-header__user-trigger:hover {
  background-color: rgba(0, 0, 0, 0.04);
  border-color: rgba(0, 0, 0, 0.12);
}

.app-header__user-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-primary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.app-header__username {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-header__dropdown-icon {
  color: var(--color-text-secondary);
  transition: transform var(--transition-base);
}

.app-header__dropdown-icon.is-open {
  transform: rotate(180deg);
}

/* Dropdown */
.app-header__dropdown {
  position: absolute;
  top: calc(100% + var(--spacing-xs));
  right: 0;
  min-width: 240px;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: var(--radius-md);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  z-index: 1001;
}

.app-header__dropdown-section {
  padding: var(--spacing-sm);
}

.app-header__dropdown-user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs);
}

.app-header__dropdown-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-primary) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.app-header__dropdown-user-details {
  flex: 1;
  min-width: 0;
}

.app-header__dropdown-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-header__dropdown-email {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-header__dropdown-divider {
  height: 1px;
  background-color: rgba(0, 0, 0, 0.06);
  margin: 0;
}

.app-header__dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  background: none;
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-base);
  text-align: left;
}

.app-header__dropdown-item:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.app-header__dropdown-item--danger {
  color: #dc2626;
}

.app-header__dropdown-item--danger:hover {
  background-color: #fef2f2;
}

/* Sign In Button */
.app-header__sign-in {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-md);
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-base);
  font-family: var(--font-family-base);
}

.app-header__sign-in:hover {
  background-color: var(--color-primary-dark, #6366f1);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

/* Dropdown Transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from {
  opacity: 0;
  transform: translateY(-8px);
}

.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .app-header {
    height: 52px;
  }

  .app-header__container {
    padding: 0 var(--spacing-md);
    gap: var(--spacing-md);
  }

  .app-header__nav {
    display: none;
  }

  .app-header__username {
    display: none;
  }

  .app-header__user-trigger {
    padding: var(--spacing-xs);
  }

  .app-header__sign-in span {
    display: none;
  }

  .app-header__dropdown {
    right: calc(-1 * var(--spacing-md));
  }
}

@media (max-width: 480px) {
  .app-header__name {
    display: none;
  }

  .app-header__logo {
    width: 28px;
    height: 28px;
  }
}
</style>
