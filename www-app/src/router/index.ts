import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import UnifiedWorkflowView from '@/views/UnifiedWorkflowView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: {
        title: 'Login - Care Circles',
        requiresAuth: false,
      },
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: () => import('@/views/AuthCallbackView.vue'),
      meta: {
        title: 'Authenticating - Care Circles',
        requiresAuth: false,
      },
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/LandingView.vue'),
      meta: {
        title: 'Care Circles - AI-Powered Care Coordination',
        requiresAuth: false,
      },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: UnifiedWorkflowView,
      meta: {
        title: 'Care Coordination - Care Circles',
        requiresAuth: true,
      },
    },
    {
      path: '/plans/:planId/edit',
      name: 'plan-edit',
      component: UnifiedWorkflowView,
      meta: {
        title: 'Edit Plan - Care Circles',
        requiresAuth: true,
      },
    },
    {
      path: '/my-plans',
      name: 'my-plans',
      component: () => import('@/views/MyPlansView.vue'),
      meta: {
        title: 'My Plans - Care Circles',
        requiresAuth: true,
      },
    },
    {
      path: '/my-tasks',
      name: 'my-tasks',
      component: () => import('@/views/MyTasksView.vue'),
      meta: {
        title: 'My Tasks - Care Circles',
        requiresAuth: true,
      },
    },
    {
      path: '/shared/:shareToken',
      name: 'shared-plan',
      component: () => import('@/views/SharedPlanView.vue'),
      meta: {
        title: 'Shared Plan - Care Circles',
        requiresAuth: false,
      },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/PlanView.vue'), // Placeholder
      meta: {
        title: 'Settings - Care Circles',
        requiresAuth: true,
      },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/PlanView.vue'), // Placeholder
      meta: {
        title: 'Profile - Care Circles',
        requiresAuth: true,
      },
    },
  ],
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  // Update page title
  document.title = (to.meta.title as string) || 'Care Circles';

  // Check authentication
  const authStore = useAuthStore();
  const requiresAuth = to.meta.requiresAuth !== false; // Default to true

  // Always ensure auth is initialized before making routing decisions
  // The initialize() function handles concurrent calls, so it's safe to call multiple times
  if (!authStore.isInitialized) {
    try {
      await authStore.initialize();
    } catch (error) {
      console.error('Auth initialization failed:', error);
      // Continue with routing even if initialization fails
    }
  }

  // If route requires auth
  if (requiresAuth) {
    // If not authenticated, redirect to landing page
    if (!authStore.isAuthenticated) {
      next({
        name: 'home',
        query: { redirect: to.fullPath },
      });
      return;
    }
  }

  // If user is authenticated and trying to access login or landing, redirect to My Plans (home)
  if ((to.name === 'login' || to.name === 'home') && authStore.isAuthenticated) {
    next({ name: 'my-plans' });
    return;
  }

  next();
});

export default router;
