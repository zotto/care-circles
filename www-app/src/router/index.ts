import { createRouter, createWebHistory } from 'vue-router';
import UnifiedWorkflowView from '@/views/UnifiedWorkflowView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: UnifiedWorkflowView,
      meta: {
        title: 'Care Coordination - Care Circles',
      },
    },
    {
      path: '/my-plans',
      name: 'my-plans',
      component: () => import('@/views/PlanView.vue'),
      meta: {
        title: 'My Plans - Care Circles',
      },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('@/views/PlanView.vue'), // Placeholder
      meta: {
        title: 'Settings - Care Circles',
      },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/PlanView.vue'), // Placeholder
      meta: {
        title: 'Profile - Care Circles',
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
router.beforeEach((to, _from, next) => {
  // Update page title
  document.title = (to.meta.title as string) || 'Care Circles';
  next();
});

export default router;
