<template>
  <div class="tasks-view">
    <div class="container">
      <div class="tasks-view__content">
        <!-- Hero Section -->
        <section class="tasks-view__header">
          <h1 class="tasks-view__title">Care Tasks</h1>
          <p class="tasks-view__subtitle">
            Review and manage your care plan
          </p>
        </section>

        <!-- Task Review Panel -->
        <section class="tasks-view__panel">
          <TaskReviewPanel
            :tasks="careStore.tasks"
            :is-loading="careStore.isLoading"
            :is-polling="careStore.isPolling"
            :job-status="careStore.activeJob?.status"
            :error="careStore.error"
            :is-approving-plan="careStore.isApprovingPlan"
            @refresh="handleRefresh"
            @update-task="handleUpdateTask"
            @delete-task="handleDeleteTask"
            @approve="handleApprove"
            @cancel="handleCancel"
          />
        </section>

        <!-- Approval processing modal -->
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
            <BaseCard class="approval-modal" @click.stop>
              <div class="approval-modal__content">
                <div class="approval-modal__icon">
                  <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                    <circle 
                      cx="32" 
                      cy="32" 
                      r="30" 
                      stroke="var(--color-success)" 
                      stroke-width="4"
                      fill="var(--color-success-light)"
                    />
                    <path 
                      d="M20 32l8 8 16-16" 
                      stroke="var(--color-success)" 
                      stroke-width="4" 
                      stroke-linecap="round" 
                      stroke-linejoin="round"
                    />
                  </svg>
                </div>

                <h2 class="approval-modal__title">{{ PLAN_APPROVAL.SUCCESS.TITLE }}</h2>
                <p class="approval-modal__message">{{ PLAN_APPROVAL.SUCCESS.MESSAGE }}</p>

                <BaseButton
                  variant="primary"
                  size="lg"
                  @click="handleCloseModal"
                  full-width
                >
                  {{ PLAN_APPROVAL.ACTIONS.DONE }}
                </BaseButton>
              </div>
            </BaseCard>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDialog
      ref="deleteDialog"
      title="Remove Task?"
      message="Are you sure you want to remove this task from the plan?"
      confirm-text="Remove Task"
      cancel-text="Keep Task"
      variant="danger"
      :icon="mdiAlertCircle"
      @confirm="confirmDelete"
      @cancel="cancelDelete"
    />

    <!-- Approval Error Dialog -->
    <ConfirmDialog
      ref="errorDialog"
      :title="PLAN_APPROVAL.ERROR.TITLE"
      :message="careStore.error || PLAN_APPROVAL.ERROR.MESSAGE"
      confirm-text="OK"
      :cancel-text="''"
      variant="danger"
      :icon="mdiAlertCircle"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import TaskReviewPanel from '@/components/organisms/TaskReviewPanel.vue';
import BaseCard from '@/components/atoms/BaseCard.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import ConfirmDialog from '@/components/organisms/ConfirmDialog.vue';
import { useCareStore } from '@/stores/careStore';
import type { CareTask } from '@/types';
import { PLAN_APPROVAL } from '@/constants';
import { mdiAlertCircle } from '@mdi/js';

const router = useRouter();
const careStore = useCareStore();
const showApprovalSuccess = ref(false);
const errorDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const deleteDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const pendingDeleteTaskId = ref<string | null>(null);

onMounted(() => {
  // If there's an active job, refresh its status
  if (careStore.currentJobId) {
    careStore.refreshJobStatus();
  }
});

onUnmounted(() => {
  // Clean up polling when leaving the page
  careStore.stopPolling();
});

watch(
  () => careStore.isApprovingPlan,
  (isApproving, wasApproving) => {
    if (wasApproving && !isApproving) {
      if (careStore.shareUrl) {
        showApprovalSuccess.value = true;
      } else if (careStore.error) {
        errorDialog.value?.open();
      }
    }
  }
);

const handleRefresh = async () => {
  await careStore.refreshJobStatus();
};

const handleUpdateTask = (taskId: string, updates: Partial<CareTask>) => {
  careStore.updateTask(taskId, updates);
};

const handleDeleteTask = (taskId: string) => {
  pendingDeleteTaskId.value = taskId;
  deleteDialog.value?.open();
};

function confirmDelete() {
  if (pendingDeleteTaskId.value) {
    careStore.deleteTask(pendingDeleteTaskId.value);
    pendingDeleteTaskId.value = null;
  }
  deleteDialog.value?.close();
}

function cancelDelete() {
  pendingDeleteTaskId.value = null;
}

const handleApprove = (planName: string) => {
  careStore.approvePlan(planName);
};

const handleCancel = () => {
  router.push('/');
};

const handleCloseModal = () => {
  showApprovalSuccess.value = false;
  // Optionally navigate to home or another page
  // router.push('/');
};
</script>

<style scoped>
.tasks-view {
  min-height: 100vh;
  padding: var(--spacing-xl) 0 var(--spacing-2xl);
}

.tasks-view__content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  max-width: 960px;
  margin: 0 auto;
}

@media (min-width: 1024px) {
  .tasks-view__content {
    max-width: 1100px;
  }
}

.tasks-view__header {
  text-align: center;
  padding: var(--spacing-xl) 0;
}

.tasks-view__title {
  font-size: clamp(2rem, 5vw, 2.5rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
}

.tasks-view__subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin: 0;
}

.tasks-view__panel {
  margin: 0;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal, 1050);
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

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.approval-modal {
  max-width: 480px;
  width: 100%;
  box-shadow: var(--shadow-2xl);
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.approval-modal__content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  text-align: center;
  padding: var(--spacing-2xl);
}

.approval-modal__icon {
  margin-bottom: var(--spacing-sm);
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
}

/* Modal Transition */
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
.modal-enter-active .approval-processing-modal,
.modal-leave-active .approval-processing-modal {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from .approval-modal,
.modal-leave-to .approval-modal,
.modal-enter-from .approval-processing-modal,
.modal-leave-to .approval-processing-modal {
  transform: scale(0.9) translateY(20px);
  opacity: 0;
}

@media (max-width: 768px) {
  .tasks-view {
    padding: var(--spacing-lg) 0;
  }

  .tasks-view__header {
    padding: var(--spacing-lg) 0;
  }
}
</style>
