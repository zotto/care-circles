<template>
  <div class="shared-plan-view">
    <div class="container">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading shared plan...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <div class="error-icon">✕</div>
        <h2>Plan Not Found</h2>
        <p class="error-message">{{ error }}</p>
      </div>

      <div v-else-if="sharedPlan" class="plan-content">
        <div class="plan-header">
          <div class="plan-header__row">
            <h1 class="plan-title">{{ sharedPlan.care_plan.summary }}</h1>
            <button
              @click="copyPlanLink"
              class="copy-link-button"
              :class="{ 'is-copied': isLinkCopied }"
              :title="isLinkCopied ? 'Link copied!' : 'Copy plan link'"
            >
              <BaseIcon 
                :path="isLinkCopied ? mdiCheck : mdiContentCopy" 
                :size="20" 
              />
            </button>
          </div>
        </div>

        <div v-if="!isAuthenticated" class="auth-prompt">
          <p>Sign in to claim and manage tasks from this plan</p>
          <button @click="goToLogin" class="login-button">
            Sign In
          </button>
        </div>

        <div class="tasks-section">
          <h2 class="section-title">Tasks ({{ sharedPlan.care_plan.tasks?.length || 0 }})</h2>

          <div v-if="!sharedPlan.care_plan.tasks || sharedPlan.care_plan.tasks.length === 0" class="empty-tasks">
            <p>No tasks available in this plan.</p>
          </div>

          <div v-else class="tasks-grid">
            <div
              v-for="task in sharedPlan.care_plan.tasks"
              :key="task.id"
              class="task-card"
              :class="{ 'task-claimed': task.status === 'claimed' || task.status === 'completed' }"
            >
              <div class="task-header">
                <span class="task-priority" :class="`priority-${task.priority}`">
                  {{ task.priority.toUpperCase() }}
                </span>
                <span class="task-status" :class="`status-${task.status}`">
                  {{ task.status }}
                </span>
              </div>

              <h3 class="task-title">{{ task.title }}</h3>
              <p class="task-description">{{ task.description }}</p>

              <div class="task-meta">
                <span class="task-category">{{ task.category }}</span>
              </div>

              <div v-if="isAuthenticated && task.status === 'available'" class="task-actions">
                <button @click="handleClaimTask(task.id)" class="claim-button">
                  Claim Task
                </button>
              </div>

              <div v-else-if="task.status === 'claimed' || task.status === 'completed'" class="task-claimed-info">
                <span class="claimed-label">
                  {{ task.status === 'completed' ? 'Completed' : 'Already claimed' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Modal -->
    <Transition name="modal">
      <div v-if="showSuccessModal" class="modal-overlay" @click="handleCloseModal">
        <div class="success-modal" @click.stop>
          <div class="success-modal__content">
            <div class="success-modal__icon">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <circle 
                  cx="32" 
                  cy="32" 
                  r="28" 
                  stroke="var(--color-success)" 
                  stroke-width="3"
                  fill="var(--color-success-light)"
                  class="success-circle"
                />
                <path 
                  d="M20 32l8 8 16-16" 
                  stroke="var(--color-success)" 
                  stroke-width="3" 
                  stroke-linecap="round" 
                  stroke-linejoin="round"
                  class="success-checkmark"
                />
              </svg>
            </div>

            <h2 class="success-modal__title">Task Claimed Successfully!</h2>
            <p class="success-modal__message">
              You can manage this task in "My Tasks"
            </p>

            <div class="success-modal__actions">
              <button @click="goToMyTasks" class="primary-button">
                Go to My Tasks
              </button>
              <button @click="handleCloseModal" class="secondary-button">
                Stay Here
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Error Modal -->
    <Transition name="modal">
      <div v-if="showErrorModal" class="modal-overlay" @click="closeErrorModal">
        <div class="error-modal" @click.stop>
          <div class="error-modal__content">
            <div class="error-modal__icon">
              <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <circle 
                  cx="32" 
                  cy="32" 
                  r="28" 
                  stroke="var(--color-danger)" 
                  stroke-width="3"
                  fill="var(--color-danger-light)"
                />
                <path 
                  d="M24 24l16 16M40 24l-16 16" 
                  stroke="var(--color-danger)" 
                  stroke-width="3" 
                  stroke-linecap="round"
                />
              </svg>
            </div>

            <h2 class="error-modal__title">Failed to Claim Task</h2>
            <p class="error-modal__message">
              {{ errorMessage }}
            </p>

            <div class="error-modal__actions">
              <button @click="closeErrorModal" class="primary-button">
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import { useTaskStore } from '@/stores/taskStore';
import { api } from '@/services/api';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import { mdiContentCopy, mdiCheck } from '@mdi/js';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const taskStore = useTaskStore();

const isLoading = ref(true);
const error = ref<string | null>(null);
const sharedPlan = ref<any>(null);
const showSuccessModal = ref(false);
const showErrorModal = ref(false);
const errorMessage = ref('');
const isLinkCopied = ref(false);

const isAuthenticated = computed(() => authStore.isAuthenticated);

onMounted(async () => {
  await loadSharedPlan();
});

async function loadSharedPlan() {
  isLoading.value = true;
  error.value = null;

  const shareToken = route.params.shareToken as string;

  try {
    const response = await api.get(`/shares/${shareToken}`);
    sharedPlan.value = response.data;
  } catch (err: any) {
    error.value = err.message || 'This shared plan could not be found or access has been disabled.';
  } finally {
    isLoading.value = false;
  }
}

async function handleClaimTask(taskId: string) {
  if (!isAuthenticated.value) {
    goToLogin();
    return;
  }

  try {
    await taskStore.claimTask(taskId);
    
    // Reload shared plan to see updated task status
    await loadSharedPlan();
    
    // Show success modal instead of alert
    showSuccessModal.value = true;
  } catch (err: any) {
    // Show error modal instead of alert
    errorMessage.value = err.message || 'Failed to claim task';
    showErrorModal.value = true;
  }
}

function handleCloseModal() {
  showSuccessModal.value = false;
}

function closeErrorModal() {
  showErrorModal.value = false;
  errorMessage.value = '';
}

function goToMyTasks() {
  router.push({ name: 'my-tasks' });
}

function goToLogin() {
  router.push({
    name: 'login',
    query: { redirect: route.fullPath },
  });
}
</script>

<style scoped>
.shared-plan-view {
  min-height: 100vh;
  padding: var(--spacing-2xl) 0;
  background: var(--color-bg-primary);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.loading-state,
.error-state {
  text-align: center;
  padding: var(--spacing-3xl);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-lg);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  background: var(--color-danger);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
}

.error-message {
  color: var(--color-text-secondary);
}

.plan-header {
  margin-bottom: var(--spacing-2xl);
}

.plan-header__row {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.plan-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
  flex: 1;
}

.copy-link-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.copy-link-button:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-primary);
  color: var(--color-primary);
  box-shadow: var(--shadow-md);
}

.copy-link-button.is-copied {
  background: var(--color-success-light);
  border-color: var(--color-success);
  color: var(--color-success);
}

.plan-summary {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

.auth-prompt {
  background: var(--color-info-light);
  border: 1px solid var(--color-info);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.login-button {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
}

.tasks-section {
  margin-top: var(--spacing-2xl);
}

.section-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xl);
}

.empty-tasks {
  text-align: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

.task-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.task-card:hover {
  box-shadow: var(--shadow-md);
}

.task-card.task-claimed {
  opacity: 0.7;
}

.task-header {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.task-priority,
.task-status {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
}

.priority-high {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.priority-medium {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.priority-low {
  background: var(--color-success-light);
  color: var(--color-success);
}

.status-available {
  background: var(--color-success-light);
  color: var(--color-success);
}

.status-claimed {
  background: var(--color-info-light);
  color: var(--color-info);
}

.status-completed {
  background: var(--color-text-tertiary);
  color: white;
}

.task-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
}

.task-description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--spacing-md);
}

.task-meta {
  margin-bottom: var(--spacing-md);
}

.task-category {
  display: inline-block;
  padding: 4px 12px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.task-actions {
  margin-top: var(--spacing-lg);
}

.claim-button {
  width: 100%;
  padding: var(--spacing-md);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
}

.claim-button:hover {
  background: var(--color-primary-dark);
}

.task-claimed-info {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-sm);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
  text-align: center;
}

.claimed-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-lg);
}

.success-modal,
.error-modal {
  max-width: 480px;
  width: 100%;
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-2xl);
}

.success-modal__content,
.error-modal__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-2xl);
  text-align: center;
}

.success-modal__icon,
.error-modal__icon {
  margin-bottom: var(--spacing-sm);
}

.success-circle {
  animation: scaleIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.success-checkmark {
  stroke-dasharray: 40;
  stroke-dashoffset: 40;
  animation: drawCheck 0.5s 0.3s ease-out forwards;
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes drawCheck {
  to {
    stroke-dashoffset: 0;
  }
}

.success-modal__title,
.error-modal__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.success-modal__message,
.error-modal__message {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

.success-modal__actions,
.error-modal__actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  width: 100%;
  margin-top: var(--spacing-sm);
}

.primary-button,
.secondary-button {
  width: 100%;
  padding: var(--spacing-md) var(--spacing-lg);
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
}

.primary-button {
  background: var(--color-primary);
  color: white;
}

.primary-button:hover {
  background: var(--color-primary-dark);
}

.secondary-button {
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.secondary-button:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-primary-light);
  color: var(--color-text-primary);
}

/* Modal Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .success-modal,
.modal-leave-active .success-modal,
.modal-enter-active .error-modal,
.modal-leave-active .error-modal {
  transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55), opacity 0.3s ease;
}

.modal-enter-from .success-modal,
.modal-enter-from .error-modal {
  transform: scale(0.8);
  opacity: 0;
}

.modal-leave-to .success-modal,
.modal-leave-to .error-modal {
  transform: scale(0.8);
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .success-modal__actions,
  .error-modal__actions {
    flex-direction: column;
  }
}
</style>
