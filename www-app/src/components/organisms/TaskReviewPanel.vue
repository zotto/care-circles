<template>
  <BaseCard class="task-review-panel" variant="elevated">
    <div class="task-review-panel__header">
      <div class="task-review-panel__header-content">
        <h2 class="task-review-panel__title">Your Care Plan</h2>
        <p class="task-review-panel__description">
          Review and edit the tasks below. Make any adjustments needed before approving.
        </p>
      </div>
      
      <div class="task-review-panel__actions">
        <BaseButton
          variant="outline"
          size="md"
          icon
          @click="handleRefresh"
          :loading="isRefreshing"
          :disabled="isRefreshing"
        >
          <template #icon>
            <BaseIcon :path="mdiRefresh" :size="18" />
          </template>
          Refresh
        </BaseButton>
      </div>
    </div>

    <!-- Plan Name Input (Compact) -->
    <div v-if="tasks.length > 0" class="task-review-panel__plan-name">
      <BaseInput
        v-model="planName"
        label="Plan Name"
        placeholder="Enter a name for this care plan"
        :required="true"
        class="plan-name-input--compact"
      />
    </div>

    <!-- Job Status Indicator -->
    <div v-if="jobStatus" class="task-review-panel__status">
      <BaseBadge :variant="getStatusVariant(jobStatus)">
        {{ getStatusLabel(jobStatus) }}
      </BaseBadge>
      <span v-if="isPolling" class="task-review-panel__status-text">
        Processing your request...
      </span>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading || (isPolling && tasks.length === 0)" class="task-review-panel__loading">
      <BaseSkeleton v-for="i in 3" :key="i" height="120px" />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="task-review-panel__error">
      <div class="error-icon">⚠️</div>
      <p class="error-message">{{ error }}</p>
      <BaseButton variant="outline" size="sm" icon @click="handleRefresh">
        <template #icon>
          <BaseIcon :path="mdiRefresh" :size="16" />
        </template>
        Try Again
      </BaseButton>
    </div>

    <!-- Tasks List -->
    <div v-else-if="tasks.length > 0" class="task-review-panel__tasks">
      <TransitionGroup name="task-list">
        <div
          v-for="(task, index) in tasks"
          :key="task.id"
          class="task-item"
          :style="{ animationDelay: `${index * 100}ms` }"
        >
          <div class="task-item__header">
            <div class="task-item__meta">
              <BaseBadge :variant="getPriorityVariant(task.priority)">
                {{ task.priority }}
              </BaseBadge>
              <span class="task-item__category">{{ task.category }}</span>
            </div>
            <button
              type="button"
              class="task-item__delete"
              @click="handleDeleteTask(task.id)"
              title="Remove task"
            >
              <BaseIcon :path="mdiClose" :size="18" />
            </button>
          </div>

          <div class="task-item__content">
            <BaseInput
              v-model="task.title"
              label="Task Title"
              placeholder="Enter task title"
              @blur="handleTaskUpdate(task.id, { title: task.title })"
            />

            <BaseTextArea
              v-model="task.description"
              label="Description"
              placeholder="Enter task description"
              :rows="3"
              :auto-resize="true"
              @blur="handleTaskUpdate(task.id, { description: task.description })"
            />

            <div class="task-item__fields">
              <div class="task-item__field">
                <label class="task-item__label">Priority</label>
                <select
                  v-model="task.priority"
                  class="task-item__select"
                  @change="handleTaskUpdate(task.id, { priority: task.priority })"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>

              <div class="task-item__field">
                <label class="task-item__label">Category</label>
                <select
                  v-model="task.category"
                  class="task-item__select"
                  @change="handleTaskUpdate(task.id, { category: task.category })"
                >
                  <option v-for="cat in categories" :key="cat" :value="cat">
                    {{ cat }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </TransitionGroup>

      <!-- Approve Actions -->
      <div class="task-review-panel__approve">
        <p class="task-review-panel__approve-text">
          Ready to share these tasks with your helpers?
        </p>
        <div class="task-review-panel__approve-actions">
          <BaseButton
            variant="outline"
            size="lg"
            icon
            @click="$emit('cancel')"
          >
            <template #icon>
              <BaseIcon :path="mdiClose" :size="18" />
            </template>
            Cancel
          </BaseButton>
          <BaseButton
            variant="primary"
            size="lg"
            icon
            @click="handleApprove"
            :disabled="!planName || planName.trim() === '' || isApprovingPlan"
          >
            <template #icon>
              <BaseIcon :path="mdiCheck" :size="18" />
            </template>
            Approve Plan
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="task-review-panel__empty">
      <div class="empty-icon">📋</div>
      <p class="empty-message">No tasks yet. Submit a care request to get started.</p>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BaseCard from '@/components/atoms/BaseCard.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import BaseBadge from '@/components/atoms/BaseBadge.vue';
import BaseSkeleton from '@/components/atoms/BaseSkeleton.vue';
import BaseInput from '@/components/atoms/BaseInput.vue';
import BaseTextArea from '@/components/atoms/BaseTextArea.vue';
import { TASK_CATEGORIES } from '@/constants';
import type { CareTask } from '@/types';

// Icons
import { mdiRefresh, mdiClose, mdiCheck } from '@mdi/js';

interface Props {
  tasks: CareTask[];
  isLoading?: boolean;
  isPolling?: boolean;
  jobStatus?: string | null;
  error?: string | null;
  /** True while plan approval is in progress (async); disables approve button. */
  isApprovingPlan?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
  isPolling: false,
  jobStatus: null,
  error: null,
  isApprovingPlan: false,
});

const emit = defineEmits<{
  refresh: [];
  updateTask: [taskId: string, updates: Partial<CareTask>];
  deleteTask: [taskId: string];
  approve: [planName: string];
  cancel: [];
}>();

const isRefreshing = ref(false);
const categories = TASK_CATEGORIES;
const planName = ref('Care Plan');

const handleRefresh = async () => {
  isRefreshing.value = true;
  emit('refresh');
  setTimeout(() => {
    isRefreshing.value = false;
  }, 1000);
};

const handleTaskUpdate = (taskId: string, updates: Partial<CareTask>) => {
  emit('updateTask', taskId, updates);
};

const handleDeleteTask = (taskId: string) => {
  emit('deleteTask', taskId);
};

const handleApprove = () => {
  if (!planName.value || planName.value.trim() === '') {
    return;
  }
  const trimmedName = planName.value.trim();
  console.log('TaskReviewPanel: Emitting approve with plan name:', trimmedName);
  emit('approve', trimmedName);
};

const getStatusVariant = (status: string): 'default' | 'success' | 'warning' | 'danger' => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'running':
      return 'warning';
    case 'failed':
      return 'danger';
    default:
      return 'default';
  }
};

const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'queued':
      return 'Queued';
    case 'running':
      return 'Processing';
    case 'completed':
      return 'Ready for Review';
    case 'failed':
      return 'Failed';
    default:
      return 'Unknown';
  }
};

const getPriorityVariant = (priority: string): 'default' | 'success' | 'warning' | 'danger' => {
  switch (priority) {
    case 'high':
      return 'danger';
    case 'medium':
      return 'warning';
    case 'low':
      return 'success';
    default:
      return 'default';
  }
};
</script>

<style scoped>
.task-review-panel {
  max-width: 900px;
  margin: 0 auto;
  border: none;
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-xl);
}

.task-review-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl) var(--spacing-xl) var(--spacing-md);
  border-bottom: 1px solid var(--color-border-light);
}

.task-review-panel__header-content {
  flex: 1;
}

.task-review-panel__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.task-review-panel__description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.task-review-panel__actions {
  display: flex;
  gap: var(--spacing-sm);
}

.task-review-panel__status {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border-light);
}

.task-review-panel__status-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.task-review-panel__loading,
.task-review-panel__error,
.task-review-panel__empty,
.task-review-panel__tasks {
  padding: var(--spacing-xl);
}

.task-review-panel__loading {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.task-review-panel__error,
.task-review-panel__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  text-align: center;
  padding: var(--spacing-2xl);
}

.error-icon,
.empty-icon {
  font-size: 3rem;
  opacity: 0.5;
}

.error-message,
.empty-message {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.task-review-panel__tasks {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.task-item {
  padding: var(--spacing-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  animation: slideInUp 0.4s ease-out backwards;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.task-item:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-md);
}

.task-item__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.task-item__meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.task-item__category {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
}

.task-item__delete {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.task-item__delete:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.task-item__content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.task-item__fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.task-item__field {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.task-item__label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.task-item__select {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.task-item__select:hover {
  border-color: var(--color-primary-light);
}

.task-item__select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-light);
}

.task-review-panel__plan-name {
  padding: var(--spacing-md) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg-secondary);
}

.plan-name-input--compact :deep(.base-input__label) {
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-xs);
}

.plan-name-input--compact :deep(.base-input__input) {
  font-size: var(--font-size-sm);
  padding: var(--spacing-xs) var(--spacing-sm);
}

.task-review-panel__approve {
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
  text-align: center;
}

.task-review-panel__approve-text {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-lg);
}

.task-review-panel__approve-actions {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
}

/* Transition animations */
.task-list-enter-active,
.task-list-leave-active {
  transition: all 0.3s ease;
}

.task-list-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.task-list-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

.task-list-move {
  transition: transform 0.3s ease;
}

@media (max-width: 768px) {
  .task-review-panel__header {
    flex-direction: column;
    align-items: stretch;
  }

  .task-review-panel__approve-actions {
    flex-direction: column;
  }

  .task-item__fields {
    grid-template-columns: 1fr;
  }
}
</style>
