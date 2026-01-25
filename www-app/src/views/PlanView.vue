<template>
  <div class="plan-view">
    <!-- Animated Background Elements -->
    <div class="plan-view__bg-decoration">
      <div class="floating-circle floating-circle--1"></div>
      <div class="floating-circle floating-circle--2"></div>
      <div class="floating-circle floating-circle--3"></div>
    </div>

    <div class="container container-md">
      <div class="plan-view__content">
        <!-- Hero Section with Scroll Reveal -->
        <section 
          ref="heroRef" 
          class="plan-view__welcome scroll-reveal"
          :class="{ 'is-visible': heroVisible }"
        >
          <div class="plan-view__hero">
            <div class="plan-view__hero-badge animate-fadeInDown">
              <BaseIcon :path="mdiStarFourPoints" :size="20" />
              <span>AI-Powered Care Coordination</span>
            </div>
            
            <h1 class="plan-view__hero-title">
              Caregiving Made
              <span class="gradient-text"> Easier Together</span>
            </h1>
            
            <p class="plan-view__hero-subtitle">
              Let our intelligent assistant help you coordinate care tasks. Share your situation, 
              and we'll create a thoughtful plan for your community to rally around.
            </p>
          </div>

          <!-- Trust Indicators with Stagger -->
          <div class="plan-view__trust">
            <div 
              v-for="(item, index) in trustItems" 
              :key="index"
              class="plan-view__trust-item"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="plan-view__trust-icon">
                <BaseIcon :path="item.icon" :size="24" />
              </div>
              <span>{{ item.text }}</span>
            </div>
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

                <h2 class="plan-view__success-title">Request Submitted Successfully!</h2>
                <p class="plan-view__success-message">
                  Thank you for trusting us with your care situation. Our AI assistant is now 
                  analyzing your needs and creating a coordinated care plan.
                </p>

                <!-- Progress Steps -->
                <div class="plan-view__success-next">
                  <strong>What happens next?</strong>
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

                <BaseButton 
                  variant="primary" 
                  size="lg" 
                  @click="handleCreateAnother"
                  class="success-button"
                >
                  <BaseIcon :path="mdiPlus" :size="20" style="margin-right: 8px;" />
                  Create Another Plan
                </BaseButton>
              </div>
            </BaseCard>
          </section>
        </Transition>

        <!-- How It Works with Scroll Animations -->
        <section 
          v-if="!showSuccess" 
          ref="stepsRef"
          class="plan-view__how-it-works scroll-reveal"
          :class="{ 'is-visible': stepsVisible }"
        >
          <div class="section-header">
            <h2 class="plan-view__section-title">How It Works</h2>
            <div class="section-divider"></div>
          </div>

          <div class="plan-view__steps">
            <div 
              v-for="(step, index) in steps" 
              :key="index"
              class="plan-view__step"
              :style="{ animationDelay: `${index * 150}ms` }"
            >
              <div class="plan-view__step-number-wrapper">
                <div class="plan-view__step-number">{{ index + 1 }}</div>
                <div class="step-connector" v-if="index < steps.length - 1"></div>
              </div>
              <div class="plan-view__step-content">
                <div class="plan-view__step-icon">
                  <BaseIcon :path="step.icon" :size="32" />
                </div>
                <h3>{{ step.title }}</h3>
                <p>{{ step.description }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Social Proof Section -->
        <section 
          v-if="!showSuccess"
          ref="proofRef"
          class="plan-view__social-proof scroll-reveal"
          :class="{ 'is-visible': proofVisible }"
        >
          <div class="social-proof-card">
            <div class="social-proof-icon">💙</div>
            <h3>Built for caregivers, by people who understand</h3>
            <p>
              Care coordination shouldn't add to your stress. Our platform makes it 
              easy to organize help, maintain boundaries, and keep everyone informed.
            </p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import CareRequestForm from '@/components/organisms/CareRequestForm.vue';
import BaseCard from '@/components/atoms/BaseCard.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import { useCareStore } from '@/stores/careStore';
import { useScrollReveal } from '@/composables/useAnimations';
import { ANIMATION } from '@/constants';
import type { CareRequest } from '@/types';

// Material Design Icons
import { 
  mdiStarFourPoints,
  mdiShieldCheck,
  mdiEmoticonHappyOutline,
  mdiAccountGroup,
  mdiPlus,
  mdiPencilOutline,
  mdiRobotOutline,
  mdiCheckDecagram,
  mdiHumanGreeting
} from '@mdi/js';

const careStore = useCareStore();
const showSuccess = ref(false);

// Scroll reveal for different sections (refs used in template)
// @ts-expect-error - elementRef is used in template via ref attribute
const { isVisible: heroVisible, elementRef: heroRef } = useScrollReveal();
// @ts-expect-error - elementRef is used in template via ref attribute
const { isVisible: formVisible, elementRef: formRef } = useScrollReveal();
// @ts-expect-error - elementRef is used in template via ref attribute
const { isVisible: stepsVisible, elementRef: stepsRef } = useScrollReveal();
// @ts-expect-error - elementRef is used in template via ref attribute
const { isVisible: proofVisible, elementRef: proofRef } = useScrollReveal();

// Trust indicators data
const trustItems = [
  { 
    text: 'Privacy-first',
    icon: mdiShieldCheck
  },
  {
    text: 'Human-approved',
    icon: mdiEmoticonHappyOutline
  },
  {
    text: 'Community-powered',
    icon: mdiAccountGroup
  }
];

// Next steps data
const nextSteps = [
  'AI analyzes your needs and generates appropriate tasks',
  'You review and customize the care plan',
  'Approved tasks are shared with your helpers'
];

// How it works steps
const steps = [
  {
    title: 'Share Your Situation',
    description: 'Describe care needs, constraints, and important boundaries in your own words.',
    icon: mdiPencilOutline
  },
  {
    title: 'AI Creates a Plan',
    description: 'Our assistant analyzes context and generates thoughtful, coordinated tasks.',
    icon: mdiRobotOutline
  },
  {
    title: 'Review & Approve',
    description: 'You have full control. Adjust, remove, or approve what feels right to you.',
    icon: mdiCheckDecagram
  },
  {
    title: 'Community Helps',
    description: 'Approved tasks are shared with helpers who can sign up to support you.',
    icon: mdiHumanGreeting
  }
];

const handleSubmit = async (data: Omit<CareRequest, 'id' | 'care_circle_id' | 'status' | 'created_at'>) => {
  try {
    await careStore.createCareRequest(
      data.narrative,
      data.constraints,
      data.boundaries
    );
    
    showSuccess.value = true;
    
    setTimeout(() => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }, ANIMATION.SUCCESS_DELAY);
  } catch (error) {
    console.error('Failed to submit care request:', error);
  }
};

const handleCreateAnother = () => {
  showSuccess.value = false;
  setTimeout(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, ANIMATION.SUCCESS_DELAY);
};

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
  padding: var(--spacing-3xl) 0;
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
  opacity: 0.1;
  filter: blur(60px);
}

.floating-circle--1 {
  width: 400px;
  height: 400px;
  background: var(--color-primary);
  top: -100px;
  right: -100px;
  animation: float 8s ease-in-out infinite;
}

.floating-circle--2 {
  width: 300px;
  height: 300px;
  background: var(--color-secondary);
  bottom: 100px;
  left: -50px;
  animation: float 10s ease-in-out infinite reverse;
}

.floating-circle--3 {
  width: 250px;
  height: 250px;
  background: var(--color-accent);
  top: 50%;
  right: 10%;
  animation: float 12s ease-in-out infinite;
}

.plan-view__content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3xl);
}

/* Hero Section */
.plan-view__welcome {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
  padding: var(--spacing-2xl) 0;
}

.plan-view__hero {
  max-width: 800px;
  margin: 0 auto;
}

.plan-view__hero-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, #fdf2f8 100%);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
  margin-bottom: var(--spacing-xl);
  animation: fadeInDown 0.6s ease-out;
}

.plan-view__hero-badge svg {
  color: var(--color-secondary);
}

.plan-view__hero-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: var(--font-weight-bold);
  line-height: 1.1;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xl);
  letter-spacing: -0.02em;
}

.plan-view__hero-subtitle {
  font-size: clamp(1.125rem, 2vw, 1.5rem);
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0;
  font-weight: var(--font-weight-normal);
}

/* Trust Indicators */
.plan-view__trust {
  display: flex;
  justify-content: center;
  gap: var(--spacing-2xl);
  flex-wrap: wrap;
  margin-top: var(--spacing-xl);
}

.plan-view__trust-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-bg-primary);
  border: 2px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-base);
  animation: fadeInUp 0.6s ease-out backwards;
  box-shadow: var(--shadow-sm);
}

.plan-view__trust-item:hover {
  transform: translateY(-4px);
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-md);
}

.plan-view__trust-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, #fdf2f8 100%);
  border-radius: var(--radius-md);
  color: var(--color-accent);
}

/* Form Section */
.plan-view__form-section {
  margin: var(--spacing-3xl) 0;
}

/* Success State */
.plan-view__success {
  margin: var(--spacing-3xl) 0;
}

.plan-view__success-card {
  max-width: 700px;
  margin: 0 auto;
  border: none;
  box-shadow: var(--shadow-2xl);
}

.plan-view__success-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xl);
  text-align: center;
  padding: var(--spacing-3xl);
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
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0;
}

.plan-view__success-message {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0;
  max-width: 500px;
}

.plan-view__success-next {
  background: linear-gradient(135deg, var(--color-bg-secondary) 0%, var(--color-primary-subtle) 100%);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  width: 100%;
  border: 1px solid var(--color-border-light);
}

.plan-view__success-next strong {
  display: block;
  font-size: var(--font-size-xl);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
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
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

.success-button {
  margin-top: var(--spacing-md);
  display: inline-flex;
  align-items: center;
}

/* How It Works */
.plan-view__how-it-works {
  margin-top: var(--spacing-3xl);
}

.section-header {
  text-align: center;
  margin-bottom: var(--spacing-3xl);
}

.plan-view__section-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-lg);
}

.section-divider {
  width: 80px;
  height: 4px;
  background: var(--color-primary-gradient);
  margin: 0 auto;
  border-radius: var(--radius-full);
}

.plan-view__steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-2xl);
}

.plan-view__step {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  background: var(--color-bg-primary);
  border: 2px solid transparent;
  border-radius: var(--radius-xl);
  transition: all var(--transition-base);
  position: relative;
  animation: fadeInUp 0.6s ease-out backwards;
  box-shadow: var(--shadow-sm);
}

.plan-view__step:hover {
  transform: translateY(-8px);
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-colored);
}

.plan-view__step-number-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.plan-view__step-number {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary-gradient);
  color: white;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  border-radius: var(--radius-full);
  box-shadow: var(--shadow-md);
  position: relative;
  z-index: 2;
}

.plan-view__step-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.plan-view__step-icon {
  color: var(--color-primary);
  display: flex;
}

.plan-view__step-content h3 {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.plan-view__step-content p {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0;
}

/* Social Proof */
.plan-view__social-proof {
  margin-top: var(--spacing-3xl);
  padding: var(--spacing-2xl) 0;
}

.social-proof-card {
  max-width: 700px;
  margin: 0 auto;
  padding: var(--spacing-3xl);
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, #fdf2f8 100%);
  border: 2px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  text-align: center;
  box-shadow: var(--shadow-lg);
}

.social-proof-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-lg);
  animation: float 3s ease-in-out infinite;
}

.social-proof-card h3 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.social-proof-card p {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: 1.7;
  margin: 0;
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

  .plan-view__trust {
    gap: var(--spacing-md);
  }

  .plan-view__trust-item {
    font-size: var(--font-size-sm);
    padding: var(--spacing-sm) var(--spacing-md);
  }

  .plan-view__trust-icon {
    width: 32px;
    height: 32px;
  }

  .plan-view__steps {
    grid-template-columns: 1fr;
  }

  .floating-circle {
    display: none;
  }
}
</style>
