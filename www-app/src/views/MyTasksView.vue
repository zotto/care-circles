<template>
  <div class="my-tasks-view">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">My Tasks</h1>
        <p class="page-description">Tasks you've claimed from care plans</p>
      </div>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your tasks...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p class="error-message">{{ error }}</p>
        <button @click="loadTasks" class="retry-button">Try Again</button>
      </div>

      <div v-else-if="myTasks.length === 0" class="empty-state">
        <p>You haven't claimed any tasks yet.</p>
        <p class="empty-hint">Browse shared plans to find tasks you can help with!</p>
      </div>

      <div v-else class="tasks-list">
        <div v-for="task in myTasks" :key="task.id" class="task-card">
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

          <div class="task-actions">
            <button
              v-if="task.status === 'claimed'"
              type="button"
              @click="openAddStatusDialog(task)"
              class="action-button add-status"
            >
              {{ TASK_DIARY.ADD_STATUS.LABEL }}
            </button>
            <button
              v-if="task.status === 'claimed'"
              type="button"
              @click="openCompleteDialog(task)"
              class="action-button primary"
            >
              {{ TASK_DIARY.COMPLETE.CONFIRM }}
            </button>
            <button
              v-if="task.status === 'claimed'"
              type="button"
              @click="openReleaseDialog(task)"
              class="action-button secondary"
            >
              {{ TASK_DIARY.RELEASE.CONFIRM }}
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
      variant="warning"
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
import ConfirmDialog from '@/components/organisms/ConfirmDialog.vue';
import TaskDiaryActionDialog from '@/components/organisms/TaskDiaryActionDialog.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import { TASK_DIARY } from '@/constants';
import type { CareTaskEvent } from '@/types';
import {
  mdiAlertCircleOutline,
  mdiCheckCircleOutline,
  mdiNoteTextOutline,
  mdiChevronRight,
  mdiChevronDown,
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
}

.empty-hint {
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-sm);
}

.tasks-list {
  display: grid;
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

.status-claimed {
  background: var(--color-info-light);
  color: var(--color-info);
}

.status-completed {
  background: var(--color-success-light);
  color: var(--color-success);
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
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.action-button {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  border: none;
}

.action-button.primary {
  background: var(--color-primary);
  color: white;
}

.action-button.primary:hover {
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

.action-button.add-status {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.action-button.add-status:hover {
  background: var(--color-border);
}

/* Task diary */
.task-diary-section {
  margin-top: var(--spacing-lg);
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

.spinner-sm {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
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
