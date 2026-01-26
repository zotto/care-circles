<template>
  <div class="plan-view">
    <!-- Animated Background Elements -->
    <div class="plan-view__bg-decoration">
      <div class="floating-circle floating-circle--1"></div>
      <div class="floating-circle floating-circle--2"></div>
      <div class="floating-circle floating-circle--3"></div>
    </div>

    <div class="container">
      <div class="plan-view__content">
        <!-- Hero Section with Scroll Reveal -->
        <section 
          ref="heroRef" 
          class="plan-view__welcome scroll-reveal"
          :class="{ 'is-visible': heroVisible }"
        >
          <div class="plan-view__hero">
            <h1 class="plan-view__hero-title">
              Get the <span class="gradient-text">help</span> you need
            </h1>
            
            <p class="plan-view__hero-subtitle">
              Your support squad is ready to rally around you
            </p>
          </div>
        </section>

        <!-- Main Form with Enhanced Animations -->
        <section 
          ref="formRef"
          class="plan-view__form-section scroll-reveal"
          :class="{ 'is-visible': formVisible }"
        >
          <CareRequestForm @submit="handleSubmit" />
        </section>

        <!-- Success State with Advanced Animation -->
        <Transition 
          name="success"
          @enter="onSuccessEnter"
          @leave="onSuccessLeave"
        >
          <section v-if="showSuccess" class="plan-view__success">
            <BaseCard variant="elevated" class="plan-view__success-card">
              <div class="plan-view__success-content">
                <!-- Animated Success Icon -->
                <div class="plan-view__success-icon-wrapper">
                  <div class="plan-view__success-icon">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                      <circle 
                        cx="32" 
                        cy="32" 
                        r="30" 
                        stroke="var(--color-success)" 
                        stroke-width="4"
                        fill="var(--color-success-light)"
                        class="success-circle"
                      />
                      <path 
                        d="M20 32l8 8 16-16" 
                        stroke="var(--color-success)" 
                        stroke-width="4" 
                        stroke-linecap="round" 
                        stroke-linejoin="round"
                        class="success-checkmark"
                      />
                    </svg>
                  </div>
                  <div class="success-ripple"></div>
                </div>

                <h2 class="plan-view__success-title">We're on it!</h2>
                <p class="plan-view__success-message">
                  We're creating your care plan now. Taking you to the review page...
                </p>

                <!-- Progress Steps -->
                <div class="plan-view__success-next">
                  <strong>What's happening?</strong>
                  <div class="progress-steps">
                    <div 
                      v-for="(step, index) in nextSteps" 
                      :key="index"
                      class="progress-step"
                      :style="{ animationDelay: `${(index + 1) * 200}ms` }"
                    >
                      <div class="progress-step__number">{{ index + 1 }}</div>
                      <p class="progress-step__text">{{ step }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </BaseCard>
          </section>
        </Transition>

      </div>
    </div>

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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import CareRequestForm from '@/components/organisms/CareRequestForm.vue';
import BaseCard from '@/components/atoms/BaseCard.vue';
import ConfirmDialog from '@/components/organisms/ConfirmDialog.vue';
import { useCareStore } from '@/stores/careStore';
import { useScrollReveal } from '@/composables/useAnimations';
import { ANIMATION } from '@/constants';
import type { CareRequest } from '@/types';
import { mdiAlertCircle } from '@mdi/js';

const router = useRouter();
const careStore = useCareStore();
const showSuccess = ref(false);
const errorDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const errorDialogTitle = ref('Error');
const errorDialogMessage = ref('');

// Scroll reveal for different sections (refs used in template)
// Since form is compact, make elements visible immediately
// @ts-expect-error - elementRef is used in template via ref attribute
const { isVisible: heroVisible, elementRef: heroRef } = useScrollReveal({ rootMargin: '200px' });
// @ts-expect-error - elementRef is used in template via ref attribute
const { isVisible: formVisible, elementRef: formRef } = useScrollReveal({ rootMargin: '200px' });

// Ensure page loads at the top and elements are visible immediately
onMounted(() => {
  // Scroll to top immediately
  window.scrollTo(0, 0);
  // Prevent any scroll restoration
  if ('scrollRestoration' in history) {
    history.scrollRestoration = 'manual';
  }
  // Make elements visible immediately since form is compact
  heroVisible.value = true;
  formVisible.value = true;
});

// Next steps data
const nextSteps = [
  'Analyzing your needs with AI',
  'Generating personalized tasks',
  'Preparing your care plan'
];

const handleSubmit = async (data: Omit<CareRequest, 'id' | 'care_circle_id' | 'status' | 'created_at'>) => {
  try {
    await careStore.createCareRequest(
      data.narrative,
      data.constraints,
      data.boundaries
    );
    
    showSuccess.value = true;
    
    // Navigate to tasks view after a brief delay
    setTimeout(() => {
      router.push('/tasks');
    }, 2000);
  } catch (error: any) {
    console.error('Failed to submit care request:', error);
    showError('Failed to Submit Request', error.message || 'Failed to submit care request. Please try again.');
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

const onSuccessEnter = (el: Element) => {
  const htmlEl = el as HTMLElement;
  htmlEl.style.opacity = '0';
  htmlEl.style.transform = 'scale(0.9)';
  
  setTimeout(() => {
    htmlEl.style.transition = `opacity ${ANIMATION.SLOW}ms ease-out, transform ${ANIMATION.SLOW}ms ease-out`;
    htmlEl.style.opacity = '1';
    htmlEl.style.transform = 'scale(1)';
  }, 50);
};

const onSuccessLeave = (el: Element) => {
  const htmlEl = el as HTMLElement;
  htmlEl.style.transition = `opacity ${ANIMATION.BASE}ms ease-in, transform ${ANIMATION.BASE}ms ease-in`;
  htmlEl.style.opacity = '0';
  htmlEl.style.transform = 'scale(0.9)';
};
</script>

<style scoped>
.plan-view {
  min-height: 100vh;
  padding: var(--spacing-xl) 0 var(--spacing-2xl);
  position: relative;
  overflow: hidden;
}

/* Animated Background */
.plan-view__bg-decoration {
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
  opacity: 0.08;
  filter: blur(80px);
}

.floating-circle--1 {
  width: 500px;
  height: 500px;
  background: var(--color-primary);
  top: -150px;
  right: -150px;
  animation: float 10s ease-in-out infinite;
}

.floating-circle--2 {
  width: 350px;
  height: 350px;
  background: var(--color-secondary);
  bottom: 100px;
  left: -100px;
  animation: float 12s ease-in-out infinite reverse;
}

.floating-circle--3 {
  width: 280px;
  height: 280px;
  background: var(--color-accent);
  top: 50%;
  right: 15%;
  animation: float 14s ease-in-out infinite;
}

.plan-view__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  max-width: 920px;
  margin: 0 auto;
}

/* Hero Section */
.plan-view__welcome {
  text-align: center;
  padding: var(--spacing-xl) 0 var(--spacing-lg);
  max-width: 680px;
  margin: 0 auto;
}

.plan-view__hero {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.plan-view__hero-title {
  font-size: clamp(2.25rem, 6vw, 3.5rem);
  font-weight: var(--font-weight-bold);
  line-height: 1.1;
  color: var(--color-text-primary);
  letter-spacing: -0.03em;
  margin: 0;
}

.plan-view__hero-subtitle {
  font-size: clamp(0.9375rem, 2vw, 1.125rem);
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0;
  font-weight: var(--font-weight-normal);
}

/* Form Section */
.plan-view__form-section {
  margin: 0;
}

/* Success State */
.plan-view__success {
  margin: var(--spacing-xl) 0;
}

.plan-view__success-card {
  max-width: 640px;
  margin: 0 auto;
  border: none;
  box-shadow: var(--shadow-xl);
}

.plan-view__success-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-lg);
  text-align: center;
  padding: var(--spacing-2xl);
}

.plan-view__success-icon-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.plan-view__success-icon {
  position: relative;
  z-index: 2;
}

.success-ripple {
  position: absolute;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--color-success-light);
  animation: ripple 2s ease-out infinite;
  z-index: 1;
}

@keyframes ripple {
  0% {
    transform: scale(0.8);
    opacity: 0.6;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

.success-circle {
  animation: scaleIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.success-checkmark {
  stroke-dasharray: 40;
  stroke-dashoffset: 40;
  animation: drawCheck 0.6s 0.3s ease-out forwards;
}

@keyframes drawCheck {
  to {
    stroke-dashoffset: 0;
  }
}

.plan-view__success-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.plan-view__success-message {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0;
  max-width: 460px;
}

.plan-view__success-next {
  background: var(--color-bg-secondary);
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  width: 100%;
  border: 1px solid var(--color-border-light);
}

.plan-view__success-next strong {
  display: block;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.progress-steps {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  text-align: left;
}

.progress-step {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  animation: fadeInLeft 0.5s ease-out backwards;
}

.progress-step__number {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  font-weight: var(--font-weight-bold);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
}

.progress-step__text {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.success-button {
  margin-top: var(--spacing-md);
  display: inline-flex;
  align-items: center;
}

/* Success Transition */
.success-enter-active,
.success-leave-active {
  transition: all 0.5s ease-out;
}

.success-enter-from,
.success-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Responsive */
@media (max-width: 768px) {
  .plan-view {
    padding: var(--spacing-xl) 0;
  }

  .plan-view__welcome {
    padding: var(--spacing-xl) 0;
  }

  .floating-circle {
    display: none;
  }
}
</style>
