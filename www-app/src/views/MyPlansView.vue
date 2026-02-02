<template>
  <div class="my-plans-view">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">My Plans</h1>
        <p class="page-description">Care plans you've created and their current status</p>
      </div>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your plans...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p class="error-message">{{ error }}</p>
        <button @click="loadPlans" class="retry-button">Try Again</button>
      </div>

      <div v-else-if="plans.length === 0" class="empty-state">
        <div class="empty-state__icon">
          <BaseIcon :path="mdiFileDocumentMultipleOutline" :size="48" />
        </div>
        <h2 class="empty-state__title">No Plans Yet</h2>
        <p class="empty-state__description">
          You haven't created any care plans yet. Start by submitting a care request.
        </p>
        <BaseButton variant="primary" @click="goToDashboard">
          Create Care Request
        </BaseButton>
      </div>

      <div v-else class="plans-list">
        <div v-for="plan in plans" :key="plan.id" class="plan-card">
          <div class="plan-card__header">
            <div class="plan-card__title-section">
              <h3 class="plan-card__title">{{ plan.summary || 'Care Plan' }}</h3>
              <span class="plan-card__date">
                Created {{ formatDate(plan.created_at) }}
              </span>
            </div>
            <div class="plan-card__header-right">
              <!-- Owner actions: Edit plan & tasks, Delete -->
              <template v-if="isPlanOwner(plan)">
                <button
                  type="button"
                  class="icon-button"
                  title="Edit plan and tasks"
                  @click="goToEditPlan(plan.id)"
                >
                  <BaseIcon :path="mdiPencil" :size="18" />
                </button>
                <button
                  type="button"
                  class="icon-button icon-button--danger"
                  :title="PLAN_ACTIONS.DELETE.CONFIRM"
                  @click="openDeleteConfirm(plan)"
                >
                  <BaseIcon :path="mdiDeleteOutline" :size="18" />
                </button>
              </template>
              <button
                @click="copyPlanLink(plan.id)"
                class="copy-link-button"
                :class="{ 'is-copied': copiedPlanId === plan.id }"
                :title="copiedPlanId === plan.id ? 'Link copied!' : 'Copy share link to share this plan'"
              >
                <BaseIcon 
                  :path="copiedPlanId === plan.id ? mdiCheck : mdiContentCopy" 
                  :size="16" 
                />
                <span class="copy-link-button__label">
                  {{ copiedPlanId === plan.id ? 'Link copied!' : 'Share plan' }}
                </span>
              </button>
            </div>
          </div>

          <!-- Plan completion indicator (total vs completed tasks) -->
          <div class="plan-card__completion">
            <PlanCompletionIndicator
              :total="getPlanCompletion(plan.id).total"
              :completed="getPlanCompletion(plan.id).completed"
              :loading="loadingTasks[plan.id] ?? false"
            />
          </div>

          <!-- Task Summary -->
          <div v-if="expandedPlanId === plan.id" class="plan-card__tasks">
            <div v-if="loadingTasks[plan.id]" class="loading-tasks">
              <div class="spinner-sm"></div>
              <span>Loading tasks...</span>
            </div>
            <div v-else-if="planTasks[plan.id] && planTasks[plan.id]!.length > 0" class="tasks-list">
              <h4 class="tasks-list__title">Tasks ({{ planTasks[plan.id]?.length || 0 }})</h4>
              <div class="task-item" v-for="task in planTasks[plan.id]!" :key="task.id">
                <div class="task-item__header">
                  <span class="task-item__priority" :class="`priority-${task.priority}`">
                    {{ task.priority.toUpperCase() }}
                  </span>
                  <span class="task-item__status" :class="`status-${task.status}`">
                    {{ formatTaskStatus(task.status) }}
                  </span>
                </div>
                <h5 class="task-item__title">{{ task.title }}</h5>
                <p class="task-item__description">{{ task.description }}</p>
                <div class="task-item__meta">
                  <span class="task-item__category">{{ task.category }}</span>
                  <span v-if="task.claimed_by" class="task-item__claimed">
                    <BaseIcon :path="mdiAccountCheck" :size="14" />
                    Claimed
                  </span>
                </div>
                <!-- Claim Button for Plan Owner -->
                <!-- Show button if user is plan owner and task is available (not claimed/completed) -->
                <div 
                  v-if="isPlanOwner(plan) && task.status === 'available' && !task.claimed_by" 
                  class="task-item__actions"
                >
                  <button
                    @click="handleClaimTask(plan.id, task.id)"
                    class="claim-button"
                    :disabled="claimingTaskId === task.id"
                  >
                    <BaseIcon :path="mdiAccountPlus" :size="16" />
                    {{ claimingTaskId === task.id ? 'Claiming...' : 'Claim Task' }}
                  </button>
                </div>
                <!-- Task diary (plan owner follow-up) -->
                <div v-if="isPlanOwner(plan)" class="task-diary-section">
                  <button
                    type="button"
                    class="task-diary-toggle"
                    :aria-expanded="expandedDiaryTaskId === task.id"
                    @click="toggleDiary(task.id)"
                  >
                    <BaseIcon
                      :path="expandedDiaryTaskId === task.id ? mdiChevronDown : mdiChevronRight"
                      :size="20"
                    />
                    <span>{{ TASK_DIARY.DIARY.TITLE }}</span>
                    <span v-if="taskEventsByTaskId[task.id]?.length" class="task-diary-count">
                      ({{ taskEventsByTaskId[task.id].length }})
                    </span>
                  </button>
                  <Transition name="diary">
                    <div v-if="expandedDiaryTaskId === task.id" class="task-diary-panel">
                      <div v-if="diaryLoadingTaskId === task.id" class="task-diary-loading">
                        <div class="spinner-sm"></div>
                        <span>Loading diary...</span>
                      </div>
                      <template v-else>
                        <p v-if="!taskEventsByTaskId[task.id]?.length" class="task-diary-empty">
                          {{ TASK_DIARY.DIARY.EMPTY }}
                        </p>
                        <ul v-else class="task-diary-list">
                          <li
                            v-for="ev in taskEventsByTaskId[task.id]"
                            :key="ev.id"
                            class="task-diary-item"
                            :class="`task-diary-item--${ev.event_type}`"
                          >
                            <span class="task-diary-item__type">
                              {{ TASK_DIARY.DIARY.EVENT_TYPES[ev.event_type] }}
                            </span>
                            <p class="task-diary-item__content">{{ ev.content }}</p>
                            <time class="task-diary-item__time" :datetime="ev.created_at">
                              {{ formatEventTime(ev.created_at) }}
                            </time>
                          </li>
                        </ul>
                      </template>
                    </div>
                  </Transition>
                </div>
              </div>
            </div>
            <div v-else class="no-tasks">
              <p>No tasks in this plan yet.</p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="plan-card__actions">
            <button
              @click="toggleTasks(plan.id)"
              class="action-button secondary"
            >
              <BaseIcon 
                :path="expandedPlanId === plan.id ? mdiChevronUp : mdiChevronDown" 
                :size="16" 
              />
              {{ expandedPlanId === plan.id ? 'Hide Tasks' : 'View Tasks' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Dialog -->
    <ConfirmDialog
      ref="successDialog"
      :title="successDialogTitle"
      :message="successDialogMessage"
      confirm-text="OK"
      :cancel-text="''"
      variant="primary"
      :icon="mdiCheckCircle"
      @confirm="closeSuccessDialog"
    />

    <!-- Error Dialog -->
    <ConfirmDialog
      ref="errorDialog"
      :title="errorDialogTitle"
      :message="errorDialogMessage"
      confirm-text="OK"
      :cancel-text="''"
      variant="danger"
      :icon="mdiAlertCircle"
      @confirm="closeErrorDialog"
    />

    <!-- Delete Plan Confirmation -->
    <ConfirmDialog
      ref="deleteDialog"
      :title="PLAN_ACTIONS.DELETE.TITLE"
      :message="PLAN_ACTIONS.DELETE.MESSAGE"
      :confirm-text="PLAN_ACTIONS.DELETE.CONFIRM"
      :cancel-text="PLAN_ACTIONS.DELETE.CANCEL"
      variant="danger"
      :icon="mdiAlertCircle"
      :loading-text="'Deleting...'"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import PlanCompletionIndicator from '@/components/atoms/PlanCompletionIndicator.vue';
import ConfirmDialog from '@/components/organisms/ConfirmDialog.vue';
import { PLAN_ACTIONS, TASK_DIARY } from '@/constants';
import type { CareTaskEvent } from '@/types';
import {
  mdiFileDocumentMultipleOutline,
  mdiChevronDown,
  mdiChevronUp,
  mdiChevronRight,
  mdiAccountCheck,
  mdiAccountPlus,
  mdiCheckCircle,
  mdiAlertCircle,
  mdiContentCopy,
  mdiCheck,
  mdiPencil,
  mdiDeleteOutline,
} from '@mdi/js';

interface CarePlan {
  id: string;
  care_request_id: string;
  summary: string;
  status: string;
  created_at: string;
  created_by: string;
}

interface CareTask {
  id: string;
  care_plan_id: string;
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  status: string;
  claimed_by?: string;
  created_at: string;
}

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const plans = ref<CarePlan[]>([]);
const planTasks = ref<Record<string, CareTask[]>>({});
const isLoading = ref(false);
const loadingTasks = ref<Record<string, boolean>>({});
const error = ref<string | null>(null);
const expandedPlanId = ref<string | null>(null);
const claimingTaskId = ref<string | null>(null);
const copiedPlanId = ref<string | null>(null);
const successDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const errorDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const deleteDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const successDialogTitle = ref('Success');
const successDialogMessage = ref('');
const errorDialogTitle = ref('Error');
const errorDialogMessage = ref('');
const pendingDeletePlanId = ref<string | null>(null);

const expandedDiaryTaskId = ref<string | null>(null);
const diaryLoadingTaskId = ref<string | null>(null);
const taskEventsByTaskId = ref<Record<string, CareTaskEvent[]>>({});

onMounted(async () => {
  await authStore.initialize();
  await loadPlans();
  // Reload when returning from plan edit
  if (route.query.updated === '1') {
    router.replace({ name: 'my-plans', query: {} });
    await loadPlans();
  }
});

async function loadPlans() {
  isLoading.value = true;
  error.value = null;

  try {
    plans.value = await api.listCarePlans();
    await loadTasksForAllPlans();
  } catch (err: any) {
    error.value = err.message || 'Failed to load plans';
  } finally {
    isLoading.value = false;
  }
}

/** Prefetch tasks for all plans so completion (total vs completed) is visible on every card. */
async function loadTasksForAllPlans() {
  if (plans.value.length === 0) return;
  for (const plan of plans.value) {
    loadingTasks.value[plan.id] = true;
  }
  await Promise.all(
    plans.value.map(async (plan) => {
      try {
        const tasks = await api.getCarePlanTasks(plan.id);
        planTasks.value[plan.id] = tasks;
      } catch {
        planTasks.value[plan.id] = [];
      } finally {
        loadingTasks.value[plan.id] = false;
      }
    })
  );
}

/** Derive plan-level completion from current task list (created/removed/updated/released all reflected). */
function getPlanCompletion(planId: string): { total: number; completed: number } {
  const tasks = planTasks.value[planId];
  if (!tasks) return { total: 0, completed: 0 };
  const total = tasks.length;
  const completed = tasks.filter((t) => t.status === 'completed').length;
  return { total, completed };
}

async function toggleTasks(planId: string) {
  if (expandedPlanId.value === planId) {
    expandedPlanId.value = null;
    return;
  }

  expandedPlanId.value = planId;

  // Load tasks if not already loaded
  if (!planTasks.value[planId]) {
    loadingTasks.value[planId] = true;
    try {
      const tasks = await api.getCarePlanTasks(planId);
      planTasks.value[planId] = tasks;
    } catch (err: any) {
      console.error('Failed to load tasks:', err);
      planTasks.value[planId] = [];
    } finally {
      loadingTasks.value[planId] = false;
    }
  }
}

async function copyPlanLink(planId: string) {
  try {
    const shareResponse = await api.generateShareLink(planId);
    const baseUrl = window.location.origin;
    const shareUrl = `${baseUrl}${shareResponse.share_url}`;

    // Copy to clipboard
    await navigator.clipboard.writeText(shareUrl);
    
    // Show visual feedback
    copiedPlanId.value = planId;
    setTimeout(() => {
      copiedPlanId.value = null;
    }, 2000);
  } catch (err: any) {
    // Show error dialog
    errorDialogTitle.value = 'Failed to share plan';
    errorDialogMessage.value = err.message || 'Failed to generate share link. Please try again.';
    errorDialog.value?.open();
  }
}

function closeSuccessDialog() {
  successDialog.value?.close();
}

function closeErrorDialog() {
  errorDialog.value?.close();
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffInMs = now.getTime() - date.getTime();
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

  if (diffInDays === 0) {
    return 'Today';
  } else if (diffInDays === 1) {
    return 'Yesterday';
  } else if (diffInDays < 7) {
    return `${diffInDays} days ago`;
  } else {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  }
}

function formatTaskStatus(status: string): string {
  const statusMap: Record<string, string> = {
    draft: 'Draft',
    available: 'Available',
    claimed: 'Claimed',
    completed: 'Completed',
  };
  return statusMap[status] || status;
}

function goToDashboard() {
  router.push('/dashboard');
}

function isPlanOwner(plan: CarePlan): boolean {
  return authStore.user?.id === plan.created_by;
}

function goToEditPlan(planId: string) {
  router.push({ name: 'plan-edit', params: { planId } });
}

function openDeleteConfirm(plan: CarePlan) {
  pendingDeletePlanId.value = plan.id;
  deleteDialog.value?.open();
}

function cancelDelete() {
  pendingDeletePlanId.value = null;
  deleteDialog.value?.close();
}

async function confirmDelete() {
  const planId = pendingDeletePlanId.value;
  if (!planId) {
    cancelDelete();
    return;
  }
  deleteDialog.value?.setLoading(true);
  try {
    await api.deleteCarePlan(planId);
    deleteDialog.value?.setLoading(false);
    cancelDelete();
    await loadPlans();
  } catch (err: any) {
    deleteDialog.value?.setLoading(false);
    errorDialogTitle.value = PLAN_ACTIONS.DELETE.ERROR_TITLE;
    errorDialogMessage.value = err.message || 'Could not delete plan. Please try again.';
    deleteDialog.value?.close();
    cancelDelete();
    errorDialog.value?.open();
  }
}

async function handleClaimTask(planId: string, taskId: string) {
  claimingTaskId.value = taskId;
  try {
    await api.post(`/tasks/${taskId}/claim`);

    const tasks = await api.getCarePlanTasks(planId);
    planTasks.value[planId] = tasks;
  } catch (err: unknown) {
    errorDialogTitle.value = 'Failed to Claim Task';
    errorDialogMessage.value = err instanceof Error ? err.message : 'Failed to claim task. Please try again.';
    errorDialog.value?.open();
  } finally {
    claimingTaskId.value = null;
  }
}

async function toggleDiary(taskId: string) {
  if (expandedDiaryTaskId.value === taskId) {
    expandedDiaryTaskId.value = null;
    return;
  }
  expandedDiaryTaskId.value = taskId;
  await loadDiaryForTask(taskId);
}

async function loadDiaryForTask(taskId: string) {
  diaryLoadingTaskId.value = taskId;
  try {
    const events = await api.getTaskEvents(taskId);
    taskEventsByTaskId.value = { ...taskEventsByTaskId.value, [taskId]: events };
  } catch {
    taskEventsByTaskId.value = { ...taskEventsByTaskId.value, [taskId]: [] };
  } finally {
    diaryLoadingTaskId.value = null;
  }
}

function formatEventTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const sameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate();
  if (sameDay) {
    return d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  }
  return d.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
}
</script>

<style scoped>
.my-plans-view {
  min-height: 100vh;
  padding: var(--spacing-2xl) 0;
  background: var(--color-bg-primary);
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

@media (min-width: 1024px) {
  .container {
    max-width: 1100px;
  }
}

.page-header {
  margin-bottom: var(--spacing-2xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.page-description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
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

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--spacing-lg);
}

.retry-button {
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-family: var(--font-family-base);
}

/* Empty State */
.empty-state__icon {
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-md);
}

.empty-state__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
}

.empty-state__description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-lg);
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

/* Plans List */
.plans-list {
  display: grid;
  gap: var(--spacing-lg);
}

.plan-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.plan-card:hover {
  box-shadow: var(--shadow-md);
}

.plan-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.plan-card__title-section {
  flex: 1;
  min-width: 0;
}

.plan-card__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.icon-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.icon-button:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.icon-button--danger:hover {
  border-color: var(--color-danger);
  color: var(--color-danger);
}

.plan-card__header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

.copy-link-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
  height: 28px;
  padding: 0 var(--spacing-sm);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-base);
  flex-shrink: 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  font-family: var(--font-family-base);
}

.copy-link-button__label {
  white-space: nowrap;
}

.copy-link-button:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.copy-link-button.is-copied {
  background: var(--color-success-light);
  border-color: var(--color-success);
  color: var(--color-success);
}

.plan-card__date {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.plan-card__completion {
  margin-bottom: var(--spacing-md);
}

.plan-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.plan-card__meta-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Tasks Section */
.plan-card__tasks {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border);
}

.loading-tasks {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
}

.spinner-sm {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.tasks-list__title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-md);
}

.task-item {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.task-item:last-child {
  margin-bottom: 0;
}

.task-item__header {
  display: flex;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-sm);
}

.task-item__priority,
.task-item__status {
  padding: 2px 8px;
  border-radius: var(--radius-sm);
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
  background: var(--color-info-light);
  color: var(--color-info);
}

.status-claimed {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.task-item__title {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.task-item__description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0 0 var(--spacing-sm);
}

.task-item__meta {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.task-item__category {
  display: inline-block;
  padding: 2px 8px;
  background: white;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.task-item__claimed {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--color-success);
}

.task-item__actions {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border);
}

.claim-button {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  font-family: var(--font-family-base);
}

.claim-button:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.claim-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Task diary (plan owner follow-up) */
.task-diary-section {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border);
}

.task-diary-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  width: 100%;
  padding: var(--spacing-sm) 0;
  background: none;
  border: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color var(--transition-base);
}

.task-diary-toggle:hover {
  color: var(--color-primary);
}

.task-diary-count {
  margin-left: var(--spacing-xs);
  color: var(--color-text-tertiary);
  font-weight: var(--font-weight-normal);
}

.task-diary-panel {
  padding: var(--spacing-md) 0 var(--spacing-md) var(--spacing-xl);
  border-left: 2px solid var(--color-border);
  margin-left: var(--spacing-sm);
}

.task-diary-loading {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.task-diary-empty {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin: 0;
}

.task-diary-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.task-diary-item {
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--color-border);
}

.task-diary-item:last-child {
  border-bottom: none;
}

.task-diary-item__type {
  display: inline-block;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-xs);
}

.task-diary-item--status_update .task-diary-item__type {
  color: var(--color-info);
}

.task-diary-item--completed .task-diary-item__type {
  color: var(--color-success);
}

.task-diary-item--released .task-diary-item__type {
  color: var(--color-warning);
}

.task-diary-item__content {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  line-height: 1.5;
  margin: 0 0 var(--spacing-xs);
}

.task-diary-item__time {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.diary-enter-active,
.diary-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.diary-enter-from,
.diary-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.no-tasks {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
}

/* Action Buttons */
.plan-card__actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.action-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  border: none;
  font-family: var(--font-family-base);
}

.action-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-button.primary {
  background: var(--color-primary);
  color: white;
}

.action-button.primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.action-button.secondary {
  background: white;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.action-button.secondary:hover {
  background: var(--color-bg-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .plan-card__header {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .plan-card__actions {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
