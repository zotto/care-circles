import { createRouter, createWebHistory } from 'vue-router';
import PlanView from '@/views/PlanView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'plan',
      component: PlanView,
      meta: {
        title: 'Create Care Plan - Care Circles',
      },
    },
    // Future routes can be added here:
    // {
    //   path: '/review/:id',
    //   name: 'review',
    //   component: () => import('@/views/ReviewView.vue'),
    //   meta: {
    //     title: 'Review Care Plan - Care Circles',
    //   },
    // },
    // {
    //   path: '/tasks/:circleId',
    //   name: 'tasks',
    //   component: () => import('@/views/TasksView.vue'),
    //   meta: {
    //     title: 'Care Tasks - Care Circles',
    //   },
    // },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// Navigation guards
router.beforeEach((to, from, next) => {
  // Update page title
  document.title = (to.meta.title as string) || 'Care Circles';
  next();
});

export default router;
