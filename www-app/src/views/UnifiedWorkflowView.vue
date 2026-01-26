<template>
  <div class="care-workflow" :class="{ 'care-workflow--focused': !requestSubmitted }">
    <!-- Background Elements -->
    <div class="care-workflow__bg-decoration">
      <div class="floating-circle floating-circle--1"></div>
      <div class="floating-circle floating-circle--2"></div>
    </div>

    <div class="container">
      <div
        class="care-workflow__content"
        :class="{ 'care-workflow__content--focused': !requestSubmitted }"
      >

        <!-- Step 1: Care Request Form -->
        <section
          v-if="!requestSubmitted"
          class="care-workflow__section care-workflow__section--focused"
        >
          <CareRequestForm @submit="handleSubmit" />
        </section>

        <!-- Step 2: Processing Status -->
        <Transition name="section">
          <section v-if="showAIAnalysisSection" class="care-workflow__section care-workflow__section--centered">
            <div class="section-header section-header--centered">
              <div class="section-badge" :class="{ 'is-complete': isJobComplete }">
                <span v-if="!isJobComplete" class="section-badge__spinner"></span>
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
                      <span v-else-if="currentStepIndex === index" class="spinner-small"></span>
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

        <!-- Step 3: Review & Approve Tasks -->
        <Transition name="section">
          <section v-if="showReviewSection" class="care-workflow__section">
            <div class="section-header section-header--centered">
              <div class="section-badge is-complete">
                <span class="section-badge__check">✓</span>
              </div>
              <div class="section-header__content">
                <h2 class="section-header__title">Your Care Plan</h2>
                <p class="section-header__description">
                  Review and customize your personalized tasks
                </p>
              </div>
            </div>

            <div class="tasks-container">
              <!-- Error State -->
              <BaseCard v-if="careStore.error" class="error-card" variant="elevated">
                <div class="error-card__content">
                  <BaseIcon :path="mdiAlertCircle" :size="48" class="error-card__icon" />
                  <h3 class="error-card__title">Unable to Generate Tasks</h3>
                  <p class="error-card__message">{{ careStore.error }}</p>
                </div>
              </BaseCard>

              <!-- Tasks List -->
              <div v-else class="tasks-list">
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
                      >
                        <BaseIcon :path="mdiClose" :size="16" />
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
                      :rows="2"
                      :auto-resize="true"
                      class="task-item__description"
                      @blur="handleTaskUpdate(task.id, { description: task.description })"
                    />

                  </div>
                </TransitionGroup>
              </div>

              <!-- Approve Actions -->
              <div class="tasks-actions">
                <div class="tasks-actions__info">
                  <BaseIcon :path="mdiInformationOutline" :size="20" />
                  <span>{{ careStore.tasks.length }} task{{ careStore.tasks.length !== 1 ? 's' : '' }} ready for approval</span>
                </div>
                <div class="tasks-actions__buttons">
                  <BaseButton
                    variant="outline"
                    size="lg"
                    @click="handleResetClick"
                  >
                    Start Over
                  </BaseButton>
                  <BaseButton
                    variant="primary"
                    size="lg"
                    @click="handleApprove"
                    :disabled="careStore.tasks.length === 0"
                  >
                    <BaseIcon :path="mdiCheckCircle" :size="20" style="margin-right: 8px;" />
                    Approve Care Plan
                  </BaseButton>
                </div>
              </div>
            </div>
          </section>
        </Transition>
      </div>
    </div>

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

            <h2 class="approval-modal__title">Care Plan Approved</h2>
            <p class="approval-modal__message">
              Your care plan has been successfully approved and is ready to share with your helpers.
            </p>

            <div class="approval-modal__actions">
              <BaseButton
                variant="primary"
                size="lg"
                @click="handleCloseModal"
                full-width
              >
                Done
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
              <BaseIcon :path="mdiAlertCircle" :size="48" />
            </div>
            <h2 class="confirm-modal__title">Remove Task</h2>
            <p class="confirm-modal__message">
              Are you sure you want to remove this task from your care plan? This action cannot be undone.
            </p>
            <div class="confirm-modal__actions">
              <BaseButton
                variant="outline"
                size="lg"
                @click="handleCloseDeleteModal"
              >
                Cancel
              </BaseButton>
              <BaseButton
                variant="danger"
                size="lg"
                @click="confirmDeleteTask"
              >
                Remove Task
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
              <BaseIcon :path="mdiAlertCircle" :size="48" />
            </div>
            <h2 class="confirm-modal__title">Start Over</h2>
            <p class="confirm-modal__message">
              Are you sure you want to start over with a new care request? This will clear all current data and cannot be undone.
            </p>
            <div class="confirm-modal__actions">
              <BaseButton
                variant="outline"
                size="lg"
                @click="handleCloseResetModal"
              >
                Cancel
              </BaseButton>
              <BaseButton
                variant="danger"
                size="lg"
                @click="confirmReset"
              >
                Start Over
              </BaseButton>
            </div>
          </div>
        </BaseCard>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import CareRequestForm from '@/components/organisms/CareRequestForm.vue';
import BaseCard from '@/components/atoms/BaseCard.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import BaseBadge from '@/components/atoms/BaseBadge.vue';
import BaseInput from '@/components/atoms/BaseInput.vue';
import BaseTextArea from '@/components/atoms/BaseTextArea.vue';
import { useCareStore } from '@/stores/careStore';
import type { CareRequest, CareTask } from '@/types';
import { PROCESSING_STEPS, TASK_PRIORITIES } from '@/constants';

// Icons
import { 
  mdiClose, 
  mdiCheckCircle, 
  mdiInformationOutline,
  mdiAlertCircle,
  mdiChevronDown
} from '@mdi/js';

const careStore = useCareStore();
const requestSubmitted = ref(false);
const showApprovalSuccess = ref(false);
const isPlanApproved = ref(false);
const activePriorityDropdown = ref<string | null>(null);
const showDeleteModal = ref(false);
const showResetModal = ref(false);
const taskToDelete = ref<string | null>(null);

const currentStepIndex = computed(() => {
  if (!careStore.activeJob) return -1;
  
  const currentAgent = careStore.activeJob.current_agent;
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

const showReviewSection = computed(() => {
  return requestSubmitted.value && isJobComplete.value && careStore.hasTasks();
});

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

// Watch requestSubmitted and scroll when transitioning
watch(requestSubmitted, (submitted) => {
  // Keep at top when transitioning
  if (submitted) {
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  }
});

onMounted(() => {
  window.scrollTo(0, 0);
  if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
  }
  // Close dropdowns when clicking outside
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  careStore.stopPolling();
  document.removeEventListener('click', handleClickOutside);
});

const handleClickOutside = () => {
  activePriorityDropdown.value = null;
};

const handleSubmit = async (data: Omit<CareRequest, 'id' | 'care_circle_id' | 'status' | 'created_at'>) => {
  try {
    await careStore.createCareRequest(
      data.narrative,
      data.constraints,
      data.boundaries
    );
    
    requestSubmitted.value = true;
    
    // Keep at top
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, 100);
  } catch (error) {
    console.error('Failed to submit care request:', error);
    alert('Failed to submit care request. Please try again.');
  }
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
  showApprovalSuccess.value = true;
  isPlanApproved.value = true;
};

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
  min-height: 100svh;
  padding: var(--spacing-2xl) 0 var(--spacing-3xl);
  position: relative;
  box-sizing: border-box;
  background: linear-gradient(to bottom, var(--color-bg-secondary) 0%, var(--color-bg-primary) 100%);
}

.care-workflow--focused {
  padding: var(--spacing-lg) 0;
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
  gap: var(--spacing-lg);
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
  gap: var(--spacing-md);
  padding: 0;
}

.section-badge {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  background: var(--color-bg-primary);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-secondary);
  transition: all var(--transition-base);
  position: relative;
}

.section-badge.is-complete {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
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
  font-size: 1.5rem;
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
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}

.status-progress__step.is-active {
  background: var(--color-primary-subtle);
}

.status-progress__step.is-complete {
  opacity: 0.7;
}

.status-progress__icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--color-bg-tertiary);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  transition: all var(--transition-base);
}

.status-progress__step.is-active .status-progress__icon {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.status-progress__step.is-complete .status-progress__icon {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
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
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 2px;
}

.status-progress__description {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.4;
}

.status-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

/* Tasks Container */
.tasks-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

/* Task Item - Compact Vertical Design */
.task-item {
  padding: var(--spacing-lg);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  animation: slideInUp 0.4s ease-out backwards;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
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
  gap: var(--spacing-md);
}

.task-item__badges {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
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
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.task-item__delete {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-base);
  flex-shrink: 0;
}

.task-item__delete:hover {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.task-item__title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-lg);
}

.task-item__description {
  font-size: var(--font-size-base);
}


/* Tasks Actions */
.tasks-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.tasks-actions__info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-info-light);
  border-radius: var(--radius-md);
  color: var(--color-info);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.tasks-actions__buttons {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
}

/* Error Card */
.error-card {
  border: 1px solid var(--color-error-light);
  background: var(--color-bg-primary);
}

.error-card__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-2xl);
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

.approval-modal__actions {
  width: 100%;
  margin-top: var(--spacing-sm);
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
.modal-leave-active .approval-modal {
  transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55), opacity 0.3s ease;
}

.modal-enter-from .approval-modal {
  transform: scale(0.8);
  opacity: 0;
}

.modal-leave-to .approval-modal {
  transform: scale(0.8);
  opacity: 0;
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

  .tasks-list {
    padding: 0 var(--spacing-sm);
  }

  .tasks-actions__buttons {
    flex-direction: column;
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
}

@media (prefers-reduced-motion: reduce) {
  .floating-circle {
    animation: none;
    opacity: 0.2;
  }
}
</style>
