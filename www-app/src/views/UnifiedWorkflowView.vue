<template>
  <div class="care-workflow" :class="{ 'care-workflow--focused': !requestSubmitted && !editMode }">
    <!-- Background Elements -->
    <div class="care-workflow__bg-decoration">
      <div class="floating-circle floating-circle--1"></div>
      <div class="floating-circle floating-circle--2"></div>
    </div>

    <div class="container">
      <div
        class="care-workflow__content"
        :class="{ 'care-workflow__content--focused': !requestSubmitted && !editMode }"
      >

        <!-- Step 1: Care Request Form (hidden in edit mode) -->
        <section
          v-if="!editMode && !requestSubmitted"
          class="care-workflow__section care-workflow__section--focused"
        >
          <CareRequestForm @submit="handleSubmit" />
        </section>

        <!-- Step 2: Processing Status (hidden in edit mode) -->
        <Transition name="section">
          <section v-if="showAIAnalysisSection && !editMode" class="care-workflow__section care-workflow__section--centered">
            <div class="section-header section-header--centered">
              <div class="section-badge" :class="{ 'is-complete': isJobComplete }">
                <LoadingSpinner v-if="!isJobComplete" size="sm" variant="white" />
                <span v-else class="section-badge__check">✓</span>
              </div>
              <div class="section-header__content">
                <h2 class="section-header__title">Analyzing Your Request</h2>
                <p class="section-header__description">
                  Creating your personalized care plan
                </p>
              </div>
            </div>

            <BaseCard class="status-card" variant="elevated">
              <div class="status-card__content">
                <div class="status-progress">
                  <div 
                    v-for="(step, index) in PROCESSING_STEPS" 
                    :key="index"
                    class="status-progress__step"
                    :class="{
                      'is-active': currentStepIndex === index,
                      'is-complete': getAgentStatus(step.agent) === 'completed'
                    }"
                  >
                    <div class="status-progress__icon">
                      <span v-if="getAgentStatus(step.agent) === 'completed'">✓</span>
                      <LoadingSpinner v-else-if="currentStepIndex === index" size="sm" variant="white" />
                      <span v-else>{{ index + 1 }}</span>
                    </div>
                    <div class="status-progress__content">
                      <h3 class="status-progress__title">{{ step.title }}</h3>
                      <p class="status-progress__description">{{ step.description }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>
          </section>
        </Transition>

        <!-- Step 3: Review & Approve / Edit Plan -->
        <Transition name="section">
          <section v-if="showReviewSection" class="care-workflow__section">
            <!-- Edit mode: loading plan -->
            <LoadingState v-if="editMode && !editPlanLoaded && !editPlanError" text="Loading plan..." compact />
            
            <ErrorState
              v-else-if="editMode && editPlanError"
              :message="editPlanError"
              :icon="mdiAlertCircle"
              title="Unable to Load Plan"
              compact
            >
              <template #action>
                <BaseButton variant="outline" size="md" icon @click="router.push({ name: 'my-plans' })">
                  <template #icon>
                    <BaseIcon :path="mdiArrowLeft" :size="18" />
                  </template>
                  Back
                </BaseButton>
              </template>
            </ErrorState>

            <!-- Error State (create flow or edit loaded) -->
            <ErrorState
              v-if="showPlanCard && careStore.error"
              :message="careStore.error"
              :icon="mdiAlertCircle"
              title="Unable to Generate Tasks"
              compact
            />

            <!-- Care Plan Card with Integrated Actions -->
            <BaseCard v-else-if="showPlanCard" class="care-plan-card" variant="elevated">
              <!-- Plan Name Input (Compact) -->
              <div class="care-plan-card__plan-name">
                <BaseInput
                  v-model="planName"
                  label="Plan Name"
                  placeholder="e.g. Post-surgery support – 3–4 weeks"
                  :required="true"
                  class="plan-name-input--compact"
                />
              </div>

              <!-- Tasks List -->
              <div class="care-plan-card__tasks">
                <TransitionGroup name="task">
                  <div
                    v-for="(task, index) in careStore.tasks"
                    :key="task.id"
                    class="task-item"
                    :style="{ animationDelay: `${index * 50}ms` }"
                  >
                    <!-- Task Header -->
                    <div class="task-item__header">
                      <div class="task-item__badges">
                        <div class="priority-badge-wrapper" @click.stop>
                          <BaseBadge 
                            :variant="getPriorityVariant(task.priority)"
                            size="sm"
                            class="priority-badge"
                            :class="{ 'priority-badge--active': activePriorityDropdown === task.id }"
                            @click="togglePriorityDropdown(task.id)"
                          >
                            {{ task.priority.toUpperCase() }}
                            <BaseIcon :path="mdiChevronDown" :size="12" class="priority-badge__icon" />
                          </BaseBadge>
                          <Transition name="dropdown">
                            <div 
                              v-if="activePriorityDropdown === task.id" 
                              class="priority-dropdown"
                              @click.stop
                            >
                              <button
                                v-for="priority in TASK_PRIORITIES"
                                :key="priority"
                                type="button"
                                class="priority-dropdown__item"
                                :class="{ 'priority-dropdown__item--active': task.priority === priority }"
                                @click="handlePriorityChange(task.id, priority as 'low' | 'medium' | 'high')"
                              >
                                {{ priority.charAt(0).toUpperCase() + priority.slice(1) }}
                              </button>
                            </div>
                          </Transition>
                        </div>
                        <span class="task-item__category">{{ task.category || 'General' }}</span>
                      </div>
                      <button
                        type="button"
                        class="task-item__delete"
                        @click="handleDeleteTaskClick(task.id)"
                        title="Remove task"
                        aria-label="Remove task"
                      >
                        <BaseIcon :path="mdiDelete" :size="18" />
                      </button>
                    </div>

                    <!-- Task Title -->
                    <BaseInput
                      v-model="task.title"
                      placeholder="Task title"
                      class="task-item__title"
                      @blur="handleTaskUpdate(task.id, { title: task.title })"
                    />

                    <!-- Task Description -->
                    <BaseTextArea
                      v-model="task.description"
                      placeholder="Task description"
                      :rows="4"
                      :auto-resize="true"
                      class="task-item__description"
                      @blur="handleTaskUpdate(task.id, { description: task.description })"
                    />
                  </div>
                </TransitionGroup>
              </div>

              <!-- Add Task -->
              <div class="care-plan-card__add-task">
                <BaseButton
                  variant="outline"
                  size="md"
                  icon
                  class="care-plan-card__add-task-btn"
                  @click="handleAddTask"
                >
                  <template #icon>
                    <BaseIcon :path="mdiPlus" :size="18" class="care-plan-card__add-task-icon" />
                  </template>
                  Add task
                </BaseButton>
              </div>

              <!-- Integrated Approve / Edit Actions Footer -->
              <div class="care-plan-card__footer">
                <div class="care-plan-card__footer-info">
                  <BaseIcon :path="mdiInformationOutline" :size="16" />
                  <span>{{ validTaskCount }} task{{ validTaskCount !== 1 ? 's' : '' }} ready</span>
                </div>
                <div class="care-plan-card__footer-actions">
                  <template v-if="editMode">
                    <BaseButton
                      variant="outline"
                      size="md"
                      icon
                      @click="handleCancelEdit"
                      :disabled="isSavingEdits"
                    >
                      <template #icon>
                        <BaseIcon :path="mdiClose" :size="18" />
                      </template>
                      Cancel
                    </BaseButton>
                    <BaseButton
                      variant="primary"
                      size="md"
                      icon
                      :loading="isSavingEdits"
                      @click="handleSavePlanEdits"
                      :disabled="validTaskCount === 0 || !planName || planName.trim() === '' || isSavingEdits"
                    >
                      <template #icon>
                        <BaseIcon :path="mdiCheck" :size="18" />
                      </template>
                      Save
                    </BaseButton>
                  </template>
                  <template v-else>
                    <BaseButton
                      variant="outline"
                      size="md"
                      icon
                      @click="handleResetClick"
                      :disabled="careStore.isApprovingPlan"
                    >
                      <template #icon>
                        <BaseIcon :path="mdiRefresh" :size="18" />
                      </template>
                      Reset
                    </BaseButton>
                    <BaseButton
                      variant="primary"
                      size="md"
                      icon
                      :loading="careStore.isApprovingPlan"
                      @click="handleApprove"
                      :disabled="validTaskCount === 0 || !planName || planName.trim() === '' || careStore.isApprovingPlan"
                    >
                      <template #icon>
                        <BaseIcon :path="mdiCheck" :size="18" />
                      </template>
                      Approve
                    </BaseButton>
                  </template>
                </div>
              </div>
            </BaseCard>
          </section>
        </Transition>
      </div>
    </div>

    <!-- Approval processing modal (non-blocking; UI stays responsive) -->
    <Transition name="modal">
      <div v-if="careStore.isApprovingPlan" class="modal-overlay modal-overlay--non-dismissible" aria-busy="true" aria-live="polite">
        <BaseCard class="approval-processing-modal" variant="elevated" @click.stop>
          <div class="approval-processing-modal__content">
            <div class="approval-processing-modal__spinner"></div>
            <h2 class="approval-processing-modal__title">{{ PLAN_APPROVAL.PROCESSING.TITLE }}</h2>
            <p class="approval-processing-modal__description">{{ PLAN_APPROVAL.PROCESSING.DESCRIPTION }}</p>
          </div>
        </BaseCard>
      </div>
    </Transition>

    <!-- Success Modal -->
    <Transition name="modal">
      <div v-if="showApprovalSuccess" class="modal-overlay" @click="handleCloseModal">
        <BaseCard class="approval-modal" variant="elevated" @click.stop>
          <div class="approval-modal__content">
            <div class="approval-modal__icon">
              <svg width="80" height="80" viewBox="0 0 80 80" fill="none">
                <circle 
                  cx="40" 
                  cy="40" 
                  r="36" 
                  stroke="var(--color-success)" 
                  stroke-width="4"
                  fill="var(--color-success-light)"
                  class="success-circle"
                />
                <path 
                  d="M25 40l10 10 20-20" 
                  stroke="var(--color-success)" 
                  stroke-width="4" 
                  stroke-linecap="round" 
                  stroke-linejoin="round"
                  class="success-checkmark"
                />
              </svg>
            </div>

            <h2 class="approval-modal__title">{{ PLAN_APPROVAL.SUCCESS.TITLE }}</h2>
            <p class="approval-modal__message">{{ PLAN_APPROVAL.SUCCESS.MESSAGE }}</p>

            <!-- Share Link Section -->
            <div v-if="planShareUrl" class="approval-modal__share">
              <label class="approval-modal__share-label">{{ PLAN_APPROVAL.SHARE.LABEL }}</label>
              <div class="approval-modal__share-box">
                <input 
                  ref="shareUrlInput"
                  type="text" 
                  :value="planShareUrl" 
                  readonly 
                  class="approval-modal__share-input"
                  @click="selectShareUrl"
                />
                <BaseButton
                  variant="outline"
                  size="sm"
                  icon
                  @click="copyShareUrl"
                  class="approval-modal__copy-btn"
                  :class="{ 'is-copied': isCopied }"
                >
                  <template #icon>
                    <BaseIcon :path="isCopied ? mdiCheck : mdiContentCopy" :size="16" />
                  </template>
                  {{ isCopied ? PLAN_APPROVAL.SHARE.COPIED_BUTTON : PLAN_APPROVAL.SHARE.COPY_BUTTON }}
                </BaseButton>
              </div>
            </div>

            <div class="approval-modal__actions">
              <BaseButton
                variant="primary"
                size="lg"
                icon
                @click="handleCloseModal"
                full-width
              >
                <template #icon>
                  <BaseIcon :path="mdiCheck" :size="20" />
                </template>
                {{ PLAN_APPROVAL.ACTIONS.DONE }}
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>
    </Transition>

    <!-- Delete Task Confirmation Modal -->
    <Transition name="modal">
      <div v-if="showDeleteModal" class="modal-overlay" @click="handleCloseDeleteModal">
        <BaseCard class="confirm-modal" variant="elevated" @click.stop>
          <div class="confirm-modal__content">
            <div class="confirm-modal__icon">
              <BaseIcon :path="mdiAlertCircle" :size="40" />
            </div>
            <h2 class="confirm-modal__title">Remove Task</h2>
            <p class="confirm-modal__message">
              Are you sure you want to remove this task from your care plan? This action cannot be undone.
            </p>
            <div class="confirm-modal__actions">
              <BaseButton
                variant="outline"
                size="md"
                icon
                @click="handleCloseDeleteModal"
              >
                <template #icon>
                  <BaseIcon :path="mdiClose" :size="18" />
                </template>
                Cancel
              </BaseButton>
              <BaseButton
                variant="danger"
                size="md"
                icon
                @click="confirmDeleteTask"
              >
                <template #icon>
                  <BaseIcon :path="mdiDeleteOutline" :size="18" />
                </template>
                Remove
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>
    </Transition>

    <!-- Start Over Confirmation Modal -->
    <Transition name="modal">
      <div v-if="showResetModal" class="modal-overlay" @click="handleCloseResetModal">
        <BaseCard class="confirm-modal" variant="elevated" @click.stop>
          <div class="confirm-modal__content">
            <div class="confirm-modal__icon">
              <BaseIcon :path="mdiAlertCircle" :size="40" />
            </div>
            <h2 class="confirm-modal__title">Start Over</h2>
            <p class="confirm-modal__message">
              Are you sure you want to start over with a new care request? This will clear all current data and cannot be undone.
            </p>
            <div class="confirm-modal__actions">
              <BaseButton
                variant="outline"
                size="md"
                icon
                @click="handleCloseResetModal"
              >
                <template #icon>
                  <BaseIcon :path="mdiClose" :size="18" />
                </template>
                Cancel
              </BaseButton>
              <BaseButton
                variant="danger"
                size="md"
                icon
                @click="confirmReset"
              >
                <template #icon>
                  <BaseIcon :path="mdiRefresh" :size="18" />
                </template>
                Reset
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>
    </Transition>

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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import CareRequestForm from '@/components/organisms/CareRequestForm.vue';
import BaseCard from '@/components/atoms/BaseCard.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import BaseBadge from '@/components/atoms/BaseBadge.vue';
import BaseInput from '@/components/atoms/BaseInput.vue';
import BaseTextArea from '@/components/atoms/BaseTextArea.vue';
import LoadingState from '@/components/atoms/LoadingState.vue';
import LoadingSpinner from '@/components/atoms/LoadingSpinner.vue';
import ErrorState from '@/components/atoms/ErrorState.vue';
import ConfirmDialog from '@/components/organisms/ConfirmDialog.vue';
import { useCareStore } from '@/stores/careStore';
import { api } from '@/services/api';
import type { CareRequest, CareTask } from '@/types';
import { PROCESSING_STEPS, TASK_PRIORITIES, PLAN_APPROVAL, CARE_PLAN } from '@/constants';
import {
  validateTasksForApproval,
  getValidTasksForSubmit,
} from '@/utils/carePlanValidation';

// Icons
import {
  mdiAlertCircle,
  mdiArrowLeft,
  mdiCheck,
  mdiChevronDown,
  mdiClose,
  mdiContentCopy,
  mdiDelete,
  mdiDeleteOutline,
  mdiInformationOutline,
  mdiPlus,
  mdiRefresh,
} from '@mdi/js';

const route = useRoute();
const router = useRouter();
const careStore = useCareStore();
const requestSubmitted = ref(false);
const showApprovalSuccess = ref(false);
const isPlanApproved = ref(false);
const planShareUrl = ref<string | null>(null);
const shareUrlInput = ref<HTMLInputElement | null>(null);
const isCopied = ref(false);
const activePriorityDropdown = ref<string | null>(null);
const showDeleteModal = ref(false);
const showResetModal = ref(false);
const errorDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const errorDialogTitle = ref('Error');
const errorDialogMessage = ref('');
const taskToDelete = ref<string | null>(null);
const planName = ref('');

// Plan edit mode (from My Plans → Edit)
const editMode = computed(() => route.name === 'plan-edit' && !!route.params.planId);
const editPlanId = computed(() => (route.params.planId as string) || '');
const editPlanLoaded = ref(false);
const editPlanError = ref<string | null>(null);
const initialServerTaskIds = ref<string[]>([]);
const isSavingEdits = ref(false);

const currentStepIndex = computed(() => {
  if (!careStore.activeJob) return -1;
  
  const currentAgent = careStore.activeJob.current_agent;
  const status = careStore.activeJob.status;
  // When job is running but current_agent not yet set, show first step as active so loading is visible (mobile + desktop)
  if (!currentAgent && (status === 'queued' || status === 'running')) {
    return 0;
  }
  if (!currentAgent) return -1;
  
  // Find the index based on current agent
  const index = PROCESSING_STEPS.findIndex(step => step.agent === currentAgent);
  return index;
});

const isJobComplete = computed(() => {
  return careStore.activeJob?.status === 'completed';
});

const showAIAnalysisSection = computed(() => {
  return requestSubmitted.value && !isJobComplete.value;
});

/** In edit mode we show the section immediately (with loading state). In create flow, only after job complete and tasks ready. */
const showReviewSection = computed(() => {
  if (editMode.value) {
    return true;
  }
  return requestSubmitted.value && isJobComplete.value && careStore.hasTasks();
});

/** Show plan card (tasks + footer) when create flow has tasks or edit mode has loaded */
const showPlanCard = computed(() => !editMode.value || editPlanLoaded.value);

/** Number of tasks that are non-empty and have title, description, and priority (ready to submit) */
const validTaskCount = computed(() => getValidTasksForSubmit(careStore.tasks ?? []).length);

const getAgentStatus = (agent: string): string => {
  if (!careStore.activeJob || !careStore.activeJob.agent_progress) {
    return 'pending';
  }
  return careStore.activeJob.agent_progress[agent] || 'pending';
};

// Auto-scroll to latest section when status changes
watch(() => careStore.activeJob?.status, (newStatus) => {
  if (newStatus === 'completed') {
    // Keep at top when completed
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 300);
  }
});

// When job completes, pre-fill plan name with agent suggestion or truncated summary
function applySuggestedPlanName() {
  if (editMode.value) return;
  const job = careStore.activeJob as { status?: string; suggested_plan_name?: string; summary?: string } | null;
  if (job?.status !== 'completed') return;
  const suggested = (job.suggested_plan_name ?? job.summary ?? '').trim();
  if (!suggested) return;
  if (!planName.value || planName.value.trim() === '') {
    planName.value = suggested.length > 60 ? `${suggested.slice(0, 57)}...` : suggested;
  }
}
watch(
  () => ({
    status: careStore.activeJob?.status,
    suggested: (careStore.activeJob as any)?.suggested_plan_name,
    summary: (careStore.activeJob as any)?.summary,
  }),
  () => applySuggestedPlanName(),
  { immediate: true }
);

// Watch requestSubmitted and scroll when transitioning
watch(requestSubmitted, (submitted) => {
  // Keep at top when transitioning
  if (submitted) {
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  }
});

// When approval finishes (async), show success modal or error dialog
watch(
  () => careStore.isApprovingPlan,
  (isApproving, wasApproving) => {
    if (wasApproving && !isApproving) {
      if (careStore.shareUrl) {
        planShareUrl.value = careStore.shareUrl;
        showApprovalSuccess.value = true;
        isPlanApproved.value = true;
      } else if (careStore.error) {
        showError(PLAN_APPROVAL.ERROR.TITLE, careStore.error || PLAN_APPROVAL.ERROR.MESSAGE);
      }
    }
  }
);

onMounted(async () => {
  window.scrollTo(0, 0);
  if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
  }
  // Close dropdowns when clicking outside
  document.addEventListener('click', handleClickOutside);

  // Edit mode: load existing plan and tasks
  if (editMode.value && editPlanId.value) {
    try {
      editPlanError.value = null;
      const plan = await api.getCarePlan(editPlanId.value);
      const tasksData = plan.tasks ?? [];
      const mappedTasks: CareTask[] = tasksData.map((t: any) => ({
        id: t.id,
        care_request_id: t.care_request_id ?? '',
        title: t.title ?? '',
        description: t.description ?? '',
        category: t.category ?? CARE_PLAN.DEFAULT_TASK_CATEGORY,
        priority: (t.priority ?? CARE_PLAN.DEFAULT_TASK_PRIORITY) as 'low' | 'medium' | 'high',
        status: t.status ?? 'draft',
        created_at: t.created_at ?? new Date().toISOString(),
      }));
      careStore.setPlanForEdit(editPlanId.value, mappedTasks);
      planName.value = (plan.summary ?? '').trim() || 'My care plan';
      initialServerTaskIds.value = mappedTasks.map((t) => t.id);
      editPlanLoaded.value = true;
    } catch (err: any) {
      editPlanError.value = err?.message ?? 'Failed to load plan';
    }
  }
});

onUnmounted(() => {
  careStore.stopPolling();
  document.removeEventListener('click', handleClickOutside);
});

const handleClickOutside = () => {
  activePriorityDropdown.value = null;
};

const handleSubmit = (data: Omit<CareRequest, 'id' | 'status' | 'created_at'>) => {
  // Show "Analyzing Your Request" immediately so the user isn't left waiting on a blank/frozen UI
  requestSubmitted.value = true;
  setTimeout(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, 100);

  // Fire the request in the background; errors are handled below
  careStore
    .createCareRequest(data.narrative, data.constraints, data.boundaries)
    .catch((error: any) => {
      console.error('Failed to submit care request:', error);
      requestSubmitted.value = false;
      showError(
        'Failed to Submit Request',
        error?.message || 'Failed to submit care request. Please try again.'
      );
    });
};

const handleTaskUpdate = (taskId: string, updates: Partial<CareTask>) => {
  careStore.updateTask(taskId, updates);
};

const togglePriorityDropdown = (taskId: string) => {
  activePriorityDropdown.value = activePriorityDropdown.value === taskId ? null : taskId;
};

const handlePriorityChange = (taskId: string, priority: 'low' | 'medium' | 'high') => {
  handleTaskUpdate(taskId, { priority });
  activePriorityDropdown.value = null;
};

const handleAddTask = () => {
  careStore.addTask();
};

const handleDeleteTaskClick = (taskId: string) => {
  taskToDelete.value = taskId;
  showDeleteModal.value = true;
};

const confirmDeleteTask = () => {
  if (taskToDelete.value) {
    careStore.deleteTask(taskToDelete.value);
    taskToDelete.value = null;
  }
  showDeleteModal.value = false;
};

const handleCloseDeleteModal = () => {
  showDeleteModal.value = false;
  taskToDelete.value = null;
};

const handleApprove = () => {
  if (!planName.value || planName.value.trim() === '') {
    return;
  }
  const validation = validateTasksForApproval(careStore.tasks ?? []);
  if (!validation.valid) {
    const nums = validation.invalidTaskNumbers;
    const taskLabel =
      nums?.length && nums.length <= 10
        ? nums.length === 1
          ? `Task #${nums[0]}`
          : `Tasks #${nums!.map((n) => n).join(', #')}`
        : null;
    const message = taskLabel
      ? `Please add a title, description, and priority to every task before approving.\n\nMissing: ${taskLabel}`
      : (validation.message ?? 'Please complete all tasks.');
    showError('Tasks incomplete', message);
    return;
  }
  const tasksToSubmit = getValidTasksForSubmit(careStore.tasks ?? []);
  careStore.approvePlan(planName.value.trim(), tasksToSubmit);
};

const handleCancelEdit = () => {
  router.push({ name: 'my-plans' });
};

const handleSavePlanEdits = async () => {
  if (!editPlanId.value || !planName.value?.trim()) return;
  const validation = validateTasksForApproval(careStore.tasks ?? []);
  if (!validation.valid) {
    const nums = validation.invalidTaskNumbers;
    const taskLabel =
      nums?.length && nums.length <= 10
        ? nums.length === 1
          ? `Task #${nums[0]}`
          : `Tasks #${nums!.map((n) => n).join(', #')}`
        : null;
    const message = taskLabel
      ? `Please add a title, description, and priority to every task before saving.\n\nMissing: ${taskLabel}`
      : (validation.message ?? 'Please complete all tasks.');
    showError('Tasks incomplete', message);
    return;
  }
  const tasksToUse = careStore.tasks ?? [];
  const validTasks = getValidTasksForSubmit(tasksToUse);
  if (validTasks.length === 0) {
    showError('No valid tasks', 'Add at least one task with title, description, and priority.');
    return;
  }
  isSavingEdits.value = true;
  try {
    await api.updateCarePlan(editPlanId.value, planName.value.trim());
    const currentIds = new Set(tasksToUse.map((t) => t.id));
    for (const task of tasksToUse) {
      const payload = {
        title: task.title.trim(),
        description: task.description.trim(),
        category: task.category || CARE_PLAN.DEFAULT_TASK_CATEGORY,
        priority: task.priority || CARE_PLAN.DEFAULT_TASK_PRIORITY,
      };
      if (task.id.startsWith('draft-')) {
        await api.addTaskToPlan(editPlanId.value, payload);
      } else {
        await api.patch(`/tasks/${task.id}`, payload);
      }
    }
    const idsToDelete = initialServerTaskIds.value.filter((id) => !currentIds.has(id));
    for (const id of idsToDelete) {
      await api.deleteCareTask(id);
    }
    router.push({ name: 'my-plans', query: { updated: '1' } });
  } catch (err: any) {
    showError('Failed to save plan', err?.message ?? 'Could not save changes. Please try again.');
  } finally {
    isSavingEdits.value = false;
  }
};

function showError(title: string, message: string) {
  errorDialogTitle.value = title;
  errorDialogMessage.value = message;
  errorDialog.value?.open();
}

function closeErrorDialog() {
  errorDialog.value?.close();
}

const handleResetClick = () => {
  // If plan is already approved, reset directly without confirmation
  if (isPlanApproved.value) {
    confirmReset();
  } else {
    // Show confirmation modal if plan hasn't been approved yet
    showResetModal.value = true;
  }
};

const confirmReset = () => {
  careStore.reset();
  requestSubmitted.value = false;
  showResetModal.value = false;
  isPlanApproved.value = false;
  planShareUrl.value = null;
  planName.value = '';
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const handleCloseResetModal = () => {
  showResetModal.value = false;
};

const handleCloseModal = () => {
  showApprovalSuccess.value = false;
  // Plan is already approved, so reset directly without confirmation
  setTimeout(() => {
    confirmReset();
  }, 300);
};

const selectShareUrl = () => {
  if (shareUrlInput.value) {
    shareUrlInput.value.select();
  }
};

const copyShareUrl = async () => {
  if (planShareUrl.value) {
    try {
      await navigator.clipboard.writeText(planShareUrl.value);
      isCopied.value = true;
      // Reset after 2 seconds
      setTimeout(() => {
        isCopied.value = false;
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      // Fallback: select the text
      selectShareUrl();
    }
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
.care-workflow {
  min-height: calc(100vh - var(--height-header));
  padding: var(--spacing-2xl) 0 var(--spacing-4xl);
  position: relative;
  box-sizing: border-box;
  background: linear-gradient(to bottom, var(--color-bg-secondary) 0%, var(--color-bg-primary) 100%);
}

.care-workflow--focused {
  padding: var(--spacing-xl) 0;
}

.care-workflow::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(600px 400px at 15% -10%, rgba(79, 70, 229, 0.08), transparent 60%),
    radial-gradient(500px 360px at 90% 10%, rgba(20, 184, 166, 0.08), transparent 55%),
    radial-gradient(520px 360px at 50% 100%, rgba(236, 72, 153, 0.06), transparent 65%);
}

.care-workflow::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.35;
  background-image: radial-gradient(rgba(15, 23, 42, 0.06) 1px, transparent 0);
  background-size: 28px 28px;
}

/* Background Decoration */
.care-workflow__bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.floating-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.05;
  filter: blur(80px);
}

.floating-circle--1 {
  width: 600px;
  height: 600px;
  background: var(--color-primary);
  top: -200px;
  right: -200px;
  animation: float 15s ease-in-out infinite;
}

.floating-circle--2 {
  width: 400px;
  height: 400px;
  background: var(--color-accent);
  bottom: -100px;
  left: -100px;
  animation: float 12s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(30px, -30px);
  }
}

.care-workflow__content {
  position: relative;
  z-index: 1;
  max-width: 1100px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
}

.care-workflow__content--focused {
  min-height: calc(100svh - var(--spacing-2xl));
  justify-content: center;
}

/* Section */
.care-workflow__section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.care-workflow__section--focused {
  align-items: center;
  width: 100%;
}

.care-workflow__section--centered {
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.section-header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-lg);
  padding: 0 var(--spacing-md);
}

.section-header--centered {
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: var(--spacing-sm);
  padding: 0;
  margin-bottom: var(--spacing-md);
}

.section-badge {
  flex-shrink: 0;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  border: 3px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: white;
  transition: all var(--transition-base);
  position: relative;
  box-shadow: var(--shadow-sm);
}

.section-badge.is-complete {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
  animation: successPop 0.5s ease-out;
}

@keyframes successPop {
  0% {
    transform: scale(0.8);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.section-badge__number {
  display: block;
}

.section-badge__spinner {
  display: block;
  width: 20px;
  height: 20px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.section-badge__check {
  font-size: var(--font-size-2xl);
  animation: checkPop 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55);
}

@keyframes checkPop {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.3);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.section-header__content {
  flex: 1;
  padding-top: var(--spacing-xs);
}

.section-header__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.section-header__description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

/* Status Card */
.status-card {
  border: none;
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-lg);
  width: 100%;
  max-width: 720px;
  margin: 0 auto;
}

.status-card__content {
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.status-progress {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.status-progress__step {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-lg);
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  opacity: 0;
  transform: translateZ(0) translateX(-30px);
  animation: slideInLeft 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
  /* Keep slide-in animation running on mobile (GPU layer) */
  will-change: transform, opacity;
}

.status-progress__step:nth-child(1) {
  animation-delay: 0.15s;
}

.status-progress__step:nth-child(2) {
  animation-delay: 0.3s;
}

.status-progress__step:nth-child(3) {
  animation-delay: 0.45s;
}

.status-progress__step:nth-child(4) {
  animation-delay: 0.6s;
}

.status-progress__step:nth-child(5) {
  animation-delay: 0.75s;
}

.status-progress__step:nth-child(6) {
  animation-delay: 0.9s;
}

@keyframes slideInLeft {
  0% {
    opacity: 0;
    transform: translateZ(0) translateX(-30px);
  }
  100% {
    opacity: 1;
    transform: translateZ(0) translateX(0);
  }
}

.status-progress__step.is-active {
  background: var(--color-primary-subtle);
  border: 1px solid var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.status-progress__step.is-complete {
  opacity: 0.7;
}

.status-progress__icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background: var(--color-bg-tertiary);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  transition: all var(--transition-base);
}

.status-progress__step.is-active .status-progress__icon {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
  box-shadow: 0 0 0 4px var(--color-primary-subtle);
  animation: pulse 2s ease-in-out infinite;
  /* Keep animation running on mobile (GPU layer) */
  will-change: transform;
  transform: translateZ(0);
  backface-visibility: hidden;
}

@keyframes pulse {
  0%, 100% {
    transform: translateZ(0) scale(1);
  }
  50% {
    transform: translateZ(0) scale(1.05);
  }
}

.status-progress__step.is-complete .status-progress__icon {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
}

.care-workflow__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--color-text-secondary);
}

.care-workflow__loading .spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

.spinner-small {
  display: block;
  width: 16px;
  height: 16px;
  border: 2px solid white;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.status-progress__content {
  flex: 1;
  padding-top: var(--spacing-xs);
}

.status-progress__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.status-progress__description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: var(--line-height-relaxed);
}

.status-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

/* Care Plan Card */
.care-plan-card {
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  border: none;
  box-shadow: var(--shadow-lg);
  font-family: var(--font-family-base);
  background: var(--color-bg-primary);
  border-radius: var(--radius-2xl);
}

.care-plan-card__plan-name {
  padding: var(--spacing-2xl) var(--spacing-2xl) 0;
}

.care-plan-card__tasks {
  padding: var(--spacing-xl) var(--spacing-2xl) var(--spacing-2xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* Task Item - Modern Design */
.task-item {
  padding: var(--spacing-xl);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
  opacity: 0;
  transform: translateY(20px);
  animation: taskSlideIn 0.4s ease-out forwards;
}

@keyframes taskSlideIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.task-item:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.task-item__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.task-item__badges {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  flex: 1;
}

.priority-badge-wrapper {
  position: relative;
  display: inline-block;
}

.priority-badge {
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  transition: all var(--transition-base);
  user-select: none;
}

.priority-badge:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.priority-badge--active {
  opacity: 0.9;
}

.priority-badge__icon {
  transition: transform var(--transition-base);
}

.priority-badge--active .priority-badge__icon {
  transform: rotate(180deg);
}

.priority-dropdown {
  position: absolute;
  top: calc(100% + var(--spacing-xs));
  left: 0;
  z-index: 10;
  min-width: 120px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  margin-top: var(--spacing-xs);
}

.priority-dropdown__item {
  display: block;
  width: 100%;
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: none;
  text-align: left;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-base);
}

.priority-dropdown__item:hover {
  background: var(--color-bg-secondary);
}

.priority-dropdown__item--active {
  background: var(--color-primary-subtle);
  color: var(--color-primary);
  font-weight: var(--font-weight-semibold);
}

.task-item__category {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  font-weight: var(--font-weight-medium);
  text-transform: capitalize;
  padding: 2px var(--spacing-xs);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
}

.task-item__delete {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-base);
  flex-shrink: 0;
  opacity: 0.6;
}

.task-item:hover .task-item__delete {
  opacity: 1;
}

.task-item__delete:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.task-item__title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  font-family: var(--font-family-base);
  letter-spacing: -0.01em;
  padding: 6px var(--spacing-sm) !important;
  min-height: auto !important;
  height: 32px !important;
  line-height: 1.4 !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-sm) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "kern" 1, "liga" 1;
}

.task-item__title::placeholder {
  font-weight: var(--font-weight-normal);
  color: var(--color-text-tertiary);
  opacity: 0.6;
}

.task-item__description {
  font-size: var(--font-size-base);
  font-family: var(--font-family-base);
  line-height: var(--line-height-relaxed);
  letter-spacing: -0.01em;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "kern" 1, "liga" 1;
}

/* Target the textarea element inside BaseTextArea */
.task-item__description :deep(.text-area__input) {
  min-height: 100px !important;
  max-height: 210px !important;
  padding: var(--spacing-sm) var(--spacing-md) !important;
  border: 1px solid var(--color-border) !important;
  border-radius: var(--radius-md) !important;
  resize: none !important;
  overflow-y: auto !important;
  transition: height 0.15s ease-out;
  height: auto !important;
}

.task-item__description::placeholder {
  font-weight: var(--font-weight-normal);
  color: var(--color-text-tertiary);
  opacity: 0.6;
}

.care-plan-card__add-task {
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px dashed var(--color-border-light);
}

.care-plan-card__add-task-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
}

@media (max-width: 768px) {
  .care-plan-card__add-task-btn {
    width: 100%;
    justify-content: center;
  }
}

.care-plan-card__add-task-icon {
  flex-shrink: 0;
}

/* Care Plan Card Footer - Integrated Actions */
.care-plan-card__plan-name {
  padding: var(--spacing-md) var(--spacing-lg);
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

.care-plan-card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border-light);
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

.care-plan-card__footer-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.care-plan-card__footer-info svg {
  color: var(--color-info);
  flex-shrink: 0;
}

.care-plan-card__footer-actions {
  display: flex;
  gap: var(--spacing-sm);
  flex-shrink: 0;
}

/* Error Card */
.error-card {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  border: 1px solid var(--color-error-light);
  background: var(--color-bg-primary);
}

.error-card__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xl);
  text-align: center;
}

.error-card__icon {
  color: var(--color-error);
}

.error-card__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.error-card__message {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

/* Modal */
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
  z-index: var(--z-modal);
  padding: var(--spacing-lg);
}

.modal-overlay--non-dismissible {
  pointer-events: auto;
  cursor: wait;
}

.approval-processing-modal {
  max-width: 420px;
  width: 100%;
  box-shadow: var(--shadow-2xl);
  border: none;
}

.approval-processing-modal__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-2xl);
  text-align: center;
}

.approval-processing-modal__spinner {
  display: block;
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.approval-processing-modal__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.approval-processing-modal__description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
}

.approval-modal {
  max-width: 520px;
  width: 100%;
  box-shadow: var(--shadow-2xl);
  border: none;
}

.approval-modal__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-2xl);
  text-align: center;
}

.approval-modal__icon {
  margin-bottom: var(--spacing-sm);
}

.success-circle {
  animation: scaleIn 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.success-checkmark {
  stroke-dasharray: 50;
  stroke-dashoffset: 50;
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

.approval-modal__title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.approval-modal__message {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
  max-width: 400px;
}

.approval-modal__share {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-md);
}

.approval-modal__share-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  text-align: left;
}

.approval-modal__share-box {
  display: flex;
  gap: var(--spacing-sm);
  width: 100%;
}

.approval-modal__share-input {
  flex: 1;
  padding: var(--spacing-sm) var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-family: var(--font-family-mono, 'Monaco', 'Courier New', monospace);
  color: var(--color-text-primary);
  background: var(--color-bg-secondary);
  cursor: text;
  transition: all var(--transition-base);
  min-width: 0; /* Allow input to shrink */
}

.approval-modal__share-input:hover {
  border-color: var(--color-primary-light);
}

.approval-modal__share-input:focus {
  outline: none;
  border-color: var(--color-primary);
  background: var(--color-bg-primary);
}

.approval-modal__copy-btn {
  flex-shrink: 0;
  transition: all var(--transition-base);
}

.approval-modal__copy-btn.is-copied {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
}

.approval-modal__actions {
  width: 100%;
  margin-top: var(--spacing-sm);
}

/* Confirm Modal (Start Over & Delete Task) - compact */
.confirm-modal {
  max-width: 380px;
  width: 100%;
  box-shadow: var(--shadow-xl);
  border: none;
  border-radius: var(--radius-md);
}

.confirm-modal__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  text-align: center;
}

.confirm-modal__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-warning, #f59e0b);
}

.confirm-modal__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
  line-height: 1.3;
}

.confirm-modal__message {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
  max-width: 100%;
}

.confirm-modal__actions {
  display: flex;
  gap: var(--spacing-sm);
  width: 100%;
  margin-top: var(--spacing-xs);
  justify-content: center;
}

.confirm-modal__actions .base-button {
  flex: 1;
  min-width: 100px;
}

/* Transitions */
.section-enter-active,
.section-leave-active {
  transition: all 0.5s ease;
}

.section-enter-from {
  opacity: 0;
  transform: translateY(30px);
}

.section-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}

.task-enter-active {
  transition: all 0.3s ease;
}

.task-leave-active {
  transition: all 0.2s ease;
  position: absolute;
}

.task-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.task-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

.task-move {
  transition: transform 0.3s ease;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .approval-modal,
.modal-leave-active .approval-modal,
.modal-enter-active .confirm-modal,
.modal-leave-active .confirm-modal {
  transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55), opacity 0.3s ease;
}

.modal-enter-from .approval-modal,
.modal-enter-from .confirm-modal {
  transform: scale(0.8);
  opacity: 0;
}

.modal-leave-to .approval-modal,
.modal-leave-to .confirm-modal {
  transform: scale(0.8);
  opacity: 0;
}

/* Desktop: use more horizontal space */
@media (min-width: 1024px) {
  .care-workflow__section--centered {
    max-width: 1100px;
  }

  .status-card {
    max-width: 1100px;
  }

  .care-plan-card {
    max-width: 1100px;
  }

  .error-card {
    max-width: 1100px;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .care-workflow {
    padding: var(--spacing-lg) 0 var(--spacing-xl);
  }

  .care-workflow--focused {
    padding: var(--spacing-md) 0;
  }

  .section-header {
    gap: var(--spacing-md);
  }

  .section-header--centered {
    gap: var(--spacing-sm);
  }

  .care-workflow__content {
    gap: var(--spacing-xl);
  }

  .section-badge {
    width: 40px;
    height: 40px;
  }

  .section-header__title {
    font-size: var(--font-size-xl);
  }

  .care-plan-card__tasks {
    padding: var(--spacing-md);
    gap: var(--spacing-xs);
  }

  .task-item {
    padding: var(--spacing-sm) var(--spacing-md);
  }

  .care-plan-card__footer {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
  }

  .care-plan-card__footer-info {
    justify-content: center;
    text-align: center;
  }

  .care-plan-card__footer-actions {
    width: 100%;
    flex-direction: column;
  }

  .care-plan-card__footer-actions .base-button {
    width: 100%;
  }

  .status-card__meta {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .status-card__content {
    padding: var(--spacing-md);
  }

  .status-progress {
    gap: var(--spacing-sm);
  }

  .status-progress__step {
    padding: var(--spacing-sm);
  }

  .approval-modal {
    max-width: calc(100% - var(--spacing-xl));
  }

  .approval-modal__content {
    padding: var(--spacing-xl);
    gap: var(--spacing-md);
  }

  .approval-modal__share-box {
    flex-direction: column;
  }

  .approval-modal__copy-btn {
    width: 100%;
  }

  .confirm-modal {
    max-width: calc(100% - var(--spacing-lg));
  }

  .confirm-modal__content {
    padding: var(--spacing-md);
    gap: var(--spacing-sm);
  }

  .confirm-modal__actions {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .confirm-modal__actions .base-button {
    width: 100%;
    min-width: unset;
  }
}

@media (prefers-reduced-motion: reduce) {
  .floating-circle {
    animation: none;
    opacity: 0.2;
  }
}
</style>
