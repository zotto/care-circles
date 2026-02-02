<template>
  <div class="my-tasks-view">
    <div class="view-container">
      <LoadingState v-if="isLoading" text="Loading your tasks..." />

      <ErrorState v-else-if="error" :message="error" :icon="mdiAlertCircle">
        <template #action>
          <BaseButton variant="primary" icon @click="loadTasks">
            <template #icon>
              <BaseIcon :path="mdiRefresh" :size="18" />
            </template>
            Try Again
          </BaseButton>
        </template>
      </ErrorState>

      <!-- Empty state -->
      <div v-else-if="myTasks.length === 0" class="empty-state-centered">
        <EmptyCard
          :icon="mdiClipboardCheckOutline"
          title="No Tasks Yet"
          description="Browse shared care plans to find tasks where you can make a difference and help others."
        />
      </div>

      <div v-else class="tasks-grid">
        <div v-for="task in myTasks" :key="task.id" class="task-card">
          <div class="task-header">
            <span class="task-priority" :class="`priority-${task.priority}`">
              {{ task.priority.toUpperCase() }}
            </span>
            <span v-if="task.status !== 'claimed'" class="task-status" :class="`status-${task.status}`">
              {{ formatTaskStatus(task.status) }}
            </span>
          </div>

          <h3 class="task-title">{{ task.title }}</h3>
          <p class="task-description">{{ task.description }}</p>

          <div class="task-meta">
            <span class="task-category">{{ task.category }}</span>
          </div>

          <div class="task-actions">
            <button
              v-if="task.status === 'claimed'"
              type="button"
              @click="openAddStatusDialog(task)"
              class="action-button add-status"
              :title="TASK_DIARY.ADD_STATUS.LABEL"
            >
              <BaseIcon :path="mdiNoteTextOutline" :size="18" class="action-button__icon" />
              <span class="action-button__text">Status</span>
            </button>
            <button
              v-if="task.status === 'claimed'"
              type="button"
              @click="openCompleteDialog(task)"
              class="action-button primary"
              :title="TASK_DIARY.COMPLETE.CONFIRM"
            >
              <BaseIcon :path="mdiCheckCircleOutline" :size="18" class="action-button__icon" />
              <span class="action-button__text">Complete</span>
            </button>
            <button
              v-if="task.status === 'claimed'"
              type="button"
              @click="openReleaseDialog(task)"
              class="action-button secondary"
              :title="TASK_DIARY.RELEASE.CONFIRM"
            >
              <BaseIcon :path="mdiAlertCircleOutline" :size="18" class="action-button__icon" />
              <span class="action-button__text">Release</span>
            </button>
          </div>

          <!-- Task diary (expandable) -->
          <div class="task-diary-section">
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
                        {{ getDiaryEventTypeLabel(ev.event_type) }}
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
    </div>

    <!-- Add status dialog -->
    <TaskDiaryActionDialog
      ref="addStatusDialog"
      :title="TASK_DIARY.ADD_STATUS.LABEL"
      :message="TASK_DIARY.ADD_STATUS.MESSAGE"
      :field-label="''"
      :field-placeholder="TASK_DIARY.ADD_STATUS.PLACEHOLDER"
      :confirm-text="TASK_DIARY.ADD_STATUS.SUBMIT"
      :cancel-text="'Cancel'"
      variant="primary"
      :icon="mdiNoteTextOutline"
      :confirm-icon="mdiContentSave"
      :max-length="TASK_DIARY.ADD_STATUS.MAX_LENGTH"
      @confirm="confirmAddStatus"
      @cancel="cancelAddStatus"
    />

    <!-- Complete task dialog (outcome required) -->
    <TaskDiaryActionDialog
      ref="completeDialog"
      :title="TASK_DIARY.COMPLETE.TITLE"
      :message="TASK_DIARY.COMPLETE.MESSAGE"
      :field-label="TASK_DIARY.COMPLETE.OUTCOME_LABEL"
      :field-placeholder="TASK_DIARY.COMPLETE.OUTCOME_PLACEHOLDER"
      :confirm-text="TASK_DIARY.COMPLETE.CONFIRM"
      :cancel-text="TASK_DIARY.COMPLETE.CANCEL"
      variant="primary"
      :icon="mdiCheckCircleOutline"
      :max-length="TASK_DIARY.COMPLETE.MAX_LENGTH"
      @confirm="confirmComplete"
      @cancel="cancelComplete"
    />

    <!-- Release task dialog (reason required) -->
    <TaskDiaryActionDialog
      ref="releaseDialog"
      :title="TASK_DIARY.RELEASE.TITLE"
      :message="TASK_DIARY.RELEASE.MESSAGE"
      :field-label="TASK_DIARY.RELEASE.REASON_LABEL"
      :field-placeholder="TASK_DIARY.RELEASE.REASON_PLACEHOLDER"
      :confirm-text="TASK_DIARY.RELEASE.CONFIRM"
      :cancel-text="TASK_DIARY.RELEASE.CANCEL"
      variant="danger"
      :icon="mdiAlertCircleOutline"
      :max-length="TASK_DIARY.RELEASE.MAX_LENGTH"
      @confirm="confirmRelease"
      @cancel="cancelRelease"
    />

    <!-- Error Dialog -->
    <ConfirmDialog
      ref="errorDialog"
      :title="errorDialogTitle"
      :message="errorDialogMessage"
      confirm-text="OK"
      :cancel-text="''"
      variant="danger"
      :icon="mdiAlertCircleOutline"
      @confirm="closeErrorDialog"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useTaskStore } from '@/stores/taskStore';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import LoadingState from '@/components/atoms/LoadingState.vue';
import EmptyCard from '@/components/atoms/EmptyCard.vue';
import ErrorState from '@/components/atoms/ErrorState.vue';
import LoadingSpinner from '@/components/atoms/LoadingSpinner.vue';
import ConfirmDialog from '@/components/organisms/ConfirmDialog.vue';
import TaskDiaryActionDialog from '@/components/organisms/TaskDiaryActionDialog.vue';
import { TASK_DIARY } from '@/constants';
import type { CareTaskEvent } from '@/types';
import {
  mdiAlertCircle,
  mdiAlertCircleOutline,
  mdiCheckCircleOutline,
  mdiChevronDown,
  mdiChevronRight,
  mdiClipboardCheckOutline,
  mdiContentSave,
  mdiNoteTextOutline,
  mdiRefresh,
} from '@mdi/js';

const taskStore = useTaskStore();

const isLoading = ref(false);
const error = ref<string | null>(null);
const addStatusDialog = ref<InstanceType<typeof TaskDiaryActionDialog> | null>(null);
const releaseDialog = ref<InstanceType<typeof TaskDiaryActionDialog> | null>(null);
const completeDialog = ref<InstanceType<typeof TaskDiaryActionDialog> | null>(null);
const errorDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const pendingTaskId = ref<string | null>(null);
const errorDialogTitle = ref('Error');
const errorDialogMessage = ref('An error occurred');

const expandedDiaryTaskId = ref<string | null>(null);
const diaryLoadingTaskId = ref<string | null>(null);
const taskEventsByTaskId = ref<Record<string, CareTaskEvent[]>>({});

const myTasks = computed(() => taskStore.myTasks);

onMounted(async () => {
  await loadTasks();
});

async function loadTasks() {
  isLoading.value = true;
  error.value = null;

  try {
    await taskStore.fetchMyTasks();
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'Failed to load tasks';
  } finally {
    isLoading.value = false;
  }
}

function openAddStatusDialog(task: { id: string }) {
  pendingTaskId.value = task.id;
  addStatusDialog.value?.open();
}

function openCompleteDialog(task: { id: string }) {
  pendingTaskId.value = task.id;
  completeDialog.value?.open();
}

function openReleaseDialog(task: { id: string }) {
  pendingTaskId.value = task.id;
  releaseDialog.value?.open();
}

async function confirmAddStatus(value: string) {
  if (!pendingTaskId.value || !addStatusDialog.value) return;

  addStatusDialog.value.setLoading(true);

  try {
    await taskStore.addTaskStatus(pendingTaskId.value, value);
    addStatusDialog.value.setLoading(false);
    addStatusDialog.value.close();
    const taskId = pendingTaskId.value;
    pendingTaskId.value = null;
    if (expandedDiaryTaskId.value === taskId) {
      await loadDiaryForTask(taskId);
    }
  } catch (err: unknown) {
    addStatusDialog.value.setLoading(false);
    addStatusDialog.value.close();
    showError(
      TASK_DIARY.ADD_STATUS.ERROR_TITLE,
      err instanceof Error ? err.message : 'Failed to add status. Please try again.'
    );
  }
}

function cancelAddStatus() {
  pendingTaskId.value = null;
}

async function confirmComplete(value: string) {
  if (!pendingTaskId.value || !completeDialog.value) return;

  completeDialog.value.setLoading(true);

  try {
    await taskStore.completeTask(pendingTaskId.value, value);
    completeDialog.value.setLoading(false);
    completeDialog.value.close();
    pendingTaskId.value = null;
  } catch (err: unknown) {
    completeDialog.value.setLoading(false);
    completeDialog.value.close();
    showError(
      TASK_DIARY.COMPLETE.ERROR_TITLE,
      err instanceof Error ? err.message : 'Failed to complete task. Please try again.'
    );
  }
}

function cancelComplete() {
  pendingTaskId.value = null;
}

async function confirmRelease(value: string) {
  if (!pendingTaskId.value || !releaseDialog.value) return;

  releaseDialog.value.setLoading(true);

  try {
    await taskStore.releaseTask(pendingTaskId.value, value);
    releaseDialog.value.setLoading(false);
    releaseDialog.value.close();
    pendingTaskId.value = null;
  } catch (err: unknown) {
    releaseDialog.value.setLoading(false);
    releaseDialog.value.close();
    showError(
      TASK_DIARY.RELEASE.ERROR_TITLE,
      err instanceof Error ? err.message : 'Failed to release task. Please try again.'
    );
  }
}

function cancelRelease() {
  pendingTaskId.value = null;
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
    const events = await taskStore.fetchTaskEvents(taskId);
    taskEventsByTaskId.value = { ...taskEventsByTaskId.value, [taskId]: events };
  } catch {
    taskEventsByTaskId.value = { ...taskEventsByTaskId.value, [taskId]: [] };
  } finally {
    diaryLoadingTaskId.value = null;
  }
}

function getDiaryEventTypeLabel(eventType: string): string {
  const labels: Record<string, string> = TASK_DIARY.DIARY.EVENT_TYPES as unknown as Record<string, string>;
  return labels[eventType] ?? eventType;
}

function formatTaskStatus(status: string): string {
  const statusMap: Record<string, string> = {
    draft: 'Draft',
    available: 'Available',
    claimed: 'Claimed',
    completed: 'Completed',
  };
  return statusMap[status] ?? status;
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

function showError(title: string, message: string) {
  errorDialogTitle.value = title;
  errorDialogMessage.value = message;
  errorDialog.value?.open();
}

function closeErrorDialog() {
  errorDialog.value?.close();
}
</script>

<style scoped>
.my-tasks-view {
  min-height: calc(100vh - var(--height-header));
  padding: var(--spacing-2xl) 0;
  background: var(--color-bg-secondary);
}

.view-container {
  max-width: var(--container-lg);
  margin: 0 auto;
  padding: 0 var(--layout-padding-desktop);
}

.empty-state-centered {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
  padding: var(--spacing-4xl) 0;
}

@media (max-width: 1024px) {
  .view-container {
    padding: 0 var(--layout-padding-tablet);
  }
}

@media (max-width: 768px) {
  .my-tasks-view {
    padding: var(--spacing-xl) 0;
  }
  
  .view-container {
    padding: 0 var(--layout-padding-mobile);
  }

  .task-card {
    padding: var(--spacing-lg);
  }

  .task-title {
    font-size: var(--font-size-xl);
    margin-bottom: var(--spacing-md);
  }

  .task-description {
    font-size: var(--font-size-base);
    margin-bottom: var(--spacing-lg);
  }

  .task-header {
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-md);
  }

  .task-priority,
  .task-status {
    padding: 0.125rem var(--spacing-sm);
    font-size: 10px;
  }

  .task-actions {
    justify-content: center;
    gap: var(--spacing-sm);
    margin-top: var(--spacing-lg);
    padding-top: var(--spacing-md);
  }
}

.tasks-grid {
  display: grid;
  gap: var(--spacing-lg);
}

.task-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-2xl);
  padding: var(--spacing-2xl);
  box-shadow: var(--shadow-card);
  transition: all var(--transition-base);
}

.task-card:hover {
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary);
  transform: translateY(-3px);
}

.task-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.task-priority,
.task-status {
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-badge);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.025em;
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

.status-claimed {
  background: var(--color-info-light);
  color: var(--color-info);
}

.status-completed {
  background: var(--color-success-light);
  color: var(--color-success);
}

.task-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg);
  line-height: var(--line-height-tight);
  letter-spacing: -0.01em;
}

.task-description {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0 0 var(--spacing-xl);
}

.task-meta {
  margin-bottom: var(--spacing-lg);
}

.task-category {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-md);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-badge);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.task-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
  flex-wrap: wrap;
}

.action-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-xl);
  border-radius: var(--radius-button);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: none;
  font-family: var(--font-family-base);
}

.action-button__icon {
  flex-shrink: 0;
}

.action-button__text {
  white-space: nowrap;
}

/* Mobile: Compact buttons */
@media (max-width: 768px) {
  .action-button {
    padding: var(--spacing-sm) var(--spacing-md);
    gap: var(--spacing-xs);
    font-size: var(--font-size-xs);
    min-height: 36px;
  }
}

.action-button.primary {
  background: var(--color-primary);
  color: white;
  box-shadow: var(--shadow-button);
}

.action-button.primary:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-button-hover);
}

.action-button.secondary {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.action-button.secondary:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.action-button.add-status {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.action-button.add-status:hover {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary);
  color: var(--color-primary);
}

/* Task diary */
.task-diary-section {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
}

.task-diary-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  width: 100%;
  padding: var(--spacing-md) 0;
  background: none;
  border: none;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color var(--transition-fast);
  font-family: var(--font-family-base);
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
  padding: var(--spacing-lg) 0 var(--spacing-md) var(--spacing-2xl);
  border-left: 2px solid var(--color-border);
  margin-left: var(--spacing-md);
}

.task-diary-loading {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  padding: var(--spacing-md) 0;
}

.task-diary-empty {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  margin: 0;
  padding: var(--spacing-md) 0;
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
  border-bottom: 1px solid var(--color-border-light, var(--color-border));
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

.task-diary-item--reopened .task-diary-item__type {
  color: var(--color-primary);
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
</style>
