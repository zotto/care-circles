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
            @refresh="handleRefresh"
            @update-task="handleUpdateTask"
            @delete-task="handleDeleteTask"
            @approve="handleApprove"
            @cancel="handleCancel"
          />
        </section>

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

                <h2 class="approval-modal__title">Plan Approved!</h2>
                <p class="approval-modal__message">
                  Your care plan has been approved and is ready to share with your helpers.
                </p>

                <BaseButton
                  variant="primary"
                  size="lg"
                  @click="handleCloseModal"
                  full-width
                >
                  Got it
                </BaseButton>
              </div>
            </BaseCard>
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import TaskReviewPanel from '@/components/organisms/TaskReviewPanel.vue';
import BaseCard from '@/components/atoms/BaseCard.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import { useCareStore } from '@/stores/careStore';
import type { CareTask } from '@/types';

const router = useRouter();
const careStore = useCareStore();
const showApprovalSuccess = ref(false);

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

const handleRefresh = async () => {
  await careStore.refreshJobStatus();
};

const handleUpdateTask = (taskId: string, updates: Partial<CareTask>) => {
  careStore.updateTask(taskId, updates);
};

const handleDeleteTask = (taskId: string) => {
  if (confirm('Are you sure you want to remove this task?')) {
    careStore.deleteTask(taskId);
  }
};

const handleApprove = () => {
  // TODO: Implement approval logic with backend
  // For now, just show success modal
  showApprovalSuccess.value = true;
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
.modal-leave-active .approval-modal {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from .approval-modal,
.modal-leave-to .approval-modal {
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
