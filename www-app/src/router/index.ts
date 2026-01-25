import { createRouter, createWebHistory } from 'vue-router';
import UnifiedWorkflowView from '@/views/UnifiedWorkflowView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'workflow',
      component: UnifiedWorkflowView,
      meta: {
        title: 'Care Coordination - Care Circles',
      },
    },
    // Keep old routes for reference/future use
    // {
    //   path: '/plan',
    //   name: 'plan',
    //   component: () => import('@/views/PlanView.vue'),
    // },
    // {
    //   path: '/tasks',
    //   name: 'tasks',
    //   component: () => import('@/views/TasksView.vue'),
    // },
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
