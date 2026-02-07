<template>
  <div class="landing-view">
    <!-- Hero Section -->
    <section class="hero" ref="heroRef">
      <div class="hero__background">
        <div class="hero__gradient"></div>
        <div class="hero__pattern"></div>
      </div>
      <div class="hero__container container">
        <div 
          class="hero__content"
          :class="{ 'is-visible': heroVisible }"
        >
          <div class="hero__badge">
            <img :src="logoUrl" alt="" class="hero__badge-logo" aria-hidden="true" />
            <span>AI-Powered Care Coordination</span>
          </div>
          <h1 class="hero__title">
            Transform Caregiving
            <span class="gradient-text">Into Action</span>
          </h1>
          <p class="hero__subtitle">
            Coordinate care by turning unstructured needs into clear, actionable tasks with AI assistance. Human-approved plans that bring care circles together.
          </p>
          <div class="hero__actions">
            <BaseButton 
              variant="primary" 
              size="lg"
              icon
              :fullWidth="isMobile"
              @click="openLoginModal"
            >
              <template #icon>
                <BaseIcon :path="mdiLogin" :size="20" />
              </template>
              Get Started
            </BaseButton>
            <BaseButton 
              variant="outline" 
              size="lg"
              icon
              :fullWidth="isMobile"
              @click="scrollToFeatures"
            >
              <template #icon>
                <BaseIcon :path="mdiChevronDown" :size="20" />
              </template>
              Learn More
            </BaseButton>
          </div>
        </div>

        <!-- Demo Video -->
        <div 
          class="hero__visual"
          :class="{ 'is-visible': heroVisible }"
        >
          <div class="hero__video-wrapper">
            <video
              class="hero__video"
              :src="demoVideoUrl"
              autoplay
              loop
              muted
              playsinline
              aria-label="Care Circles product demo"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features" id="features">
      <div class="container">
        <div 
          class="features__header scroll-reveal"
          :class="{ 'is-visible': featuresHeaderVisible }"
          ref="featuresHeaderRef"
        >
          <h2 class="features__title">Intelligent Care Coordination</h2>
          <p class="features__subtitle">
            AI intelligence combined with human oversight for comprehensive care solutions.
          </p>
        </div>

        <div class="features__grid">
          <div
            v-for="(feature, index) in features"
            :key="index"
            class="feature-card scroll-reveal"
            :class="{ 'is-visible': featureVisible[index] }"
            :ref="(el) => setFeatureRef(el, index)"
            :style="{ transitionDelay: getDelay(index) }"
          >
            <div class="feature-card__icon">
              <BaseIcon :path="feature.icon" :size="32" />
            </div>
            <h3 class="feature-card__title">{{ feature.title }}</h3>
            <p class="feature-card__description">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="how-it-works">
      <div class="container">
        <div 
          class="how-it-works__header scroll-reveal"
          :class="{ 'is-visible': howItWorksHeaderVisible }"
          ref="howItWorksHeaderRef"
        >
          <h2 class="how-it-works__title">How It Works</h2>
          <p class="how-it-works__subtitle">
            From care request to coordinated action in simple steps
          </p>
        </div>

        <div class="how-it-works__steps">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="step-card scroll-reveal"
            :class="{ 'is-visible': stepVisible[index] }"
            :ref="(el) => setStepRef(el, index)"
            :style="{ transitionDelay: getDelay(index) }"
          >
            <div class="step-card__number">{{ index + 1 }}</div>
            <h3 class="step-card__title">{{ step.title }}</h3>
            <p class="step-card__description">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="container">
        <div 
          class="cta__content scroll-reveal"
          :class="{ 'is-visible': ctaVisible }"
          ref="ctaRef"
        >
          <h2 class="cta__title">Ready to Get Started?</h2>
          <p class="cta__subtitle">
            Experience the future of care coordination
          </p>
          <BaseButton 
            variant="primary" 
            size="lg"
            icon
            :fullWidth="isMobile"
            @click="openLoginModal"
          >
            <template #icon>
              <BaseIcon :path="mdiLogin" :size="20" />
            </template>
            Get Started
          </BaseButton>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, type ComponentPublicInstance } from 'vue';
import { useScrollReveal, useStaggeredReveal } from '@/composables/useAnimations';
import { useLoginModal } from '@/composables/useLoginModal';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import {
  mdiAccountMultiple,
  mdiChevronDown,
  mdiEyeCheck,
  mdiLogin,
  mdiRobot,
  mdiShieldCheck,
} from '@mdi/js';
import logoUrl from '@/assets/logo.png';
import demoVideoUrl from '@/assets/demo.mp4';

const { open: openLoginModal } = useLoginModal();

// Mobile detection
const windowWidth = ref(window.innerWidth);
const isMobile = computed(() => windowWidth.value <= 768);

const updateWindowWidth = () => {
  windowWidth.value = window.innerWidth;
};

const scrollToFeatures = () => {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
};

// Hero animation
// @ts-expect-error - heroRef is used in template
const { isVisible: heroVisible, elementRef: heroRef } = useScrollReveal({
  threshold: 0.2,
  once: true,
});

// Features header
// @ts-expect-error - featuresHeaderRef is used in template
const { isVisible: featuresHeaderVisible, elementRef: featuresHeaderRef } = useScrollReveal({
  threshold: 0.1,
  once: true,
});

// Features grid
const featureVisible = ref<boolean[]>([]);
const featureRefs = ref<(HTMLElement | null)[]>([]);

const setFeatureRef = (el: Element | ComponentPublicInstance | null, index: number) => {
  const element = el as HTMLElement | null;
  if (element) {
    featureRefs.value[index] = element;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          featureVisible.value[index] = true;
          if (observer) observer.disconnect();
        }
      },
      { threshold: 0.1, rootMargin: '0px' }
    );
    observer.observe(element);
  }
};

// How it works header
// @ts-expect-error - howItWorksHeaderRef is used in template
const { isVisible: howItWorksHeaderVisible, elementRef: howItWorksHeaderRef } = useScrollReveal({
  threshold: 0.1,
  once: true,
});

// Steps
const stepVisible = ref<boolean[]>([]);
const stepRefs = ref<(HTMLElement | null)[]>([]);

const setStepRef = (el: Element | ComponentPublicInstance | null, index: number) => {
  const element = el as HTMLElement | null;
  if (element) {
    stepRefs.value[index] = element;
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) {
          stepVisible.value[index] = true;
          if (observer) observer.disconnect();
        }
      },
      { threshold: 0.1, rootMargin: '0px' }
    );
    observer.observe(element);
  }
};

// CTA
// @ts-expect-error - ctaRef is used in template
const { isVisible: ctaVisible, elementRef: ctaRef } = useScrollReveal({
  threshold: 0.2,
  once: true,
});

// Staggered delays
const { getDelay } = useStaggeredReveal(100);

const features = [
  {
    icon: mdiRobot,
    title: 'AI-Powered Analysis',
    description: 'Our intelligent agents understand caregiving narratives and identify needs, constraints, and priorities automatically.',
  },
  {
    icon: mdiShieldCheck,
    title: 'Human Oversight',
    description: 'Every care plan requires explicit human approval. You maintain full control over what gets published.',
  },
  {
    icon: mdiAccountMultiple,
    title: 'Care Circles',
    description: 'Coordinate with family, friends, and helpers in organized groups. Share plans and assign tasks seamlessly.',
  },
  {
    icon: mdiEyeCheck,
    title: 'Transparent Process',
    description: 'See exactly how your care request is processed. Review agent reasoning and make informed decisions.',
  },
];

const steps = [
  {
    title: 'Submit Your Request',
    description: 'Describe your caregiving situation in your own words. Our AI will understand the context and needs.',
  },
  {
    title: 'AI Analysis & Planning',
    description: 'Our agents analyze your request, identify needs, generate tasks, and ensure quality and safety.',
  },
  {
    title: 'Review & Approve',
    description: 'Review the generated care plan, edit tasks as needed, and approve when ready.',
  },
  {
    title: 'Coordinate & Execute',
    description: 'Share your approved plan with your care circle. Helpers can see and claim tasks to provide support.',
  },
];

onMounted(() => {
  // Initialize feature visibility array
  featureVisible.value = new Array(features.length).fill(false);
  stepVisible.value = new Array(steps.length).fill(false);

  // Add window resize listener
  window.addEventListener('resize', updateWindowWidth);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateWindowWidth);
});
</script>

<style scoped>
.landing-view {
  width: 100%;
  overflow-x: hidden;
}

/* Hero Section */
.hero {
  position: relative;
  min-height: 90vh;
  display: flex;
  align-items: center;
  padding: var(--spacing-4xl) 0;
  overflow: hidden;
}

.hero__background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.hero__gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    var(--color-primary-subtle) 0%,
    rgba(236, 72, 153, 0.05) 50%,
    rgba(20, 184, 166, 0.05) 100%
  );
}

.hero__pattern {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(circle at 20% 50%, rgba(79, 70, 229, 0.08) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.08) 0%, transparent 50%);
  background-size: 100% 100%;
}

.hero__container {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-5xl);
  align-items: center;
}

.hero__content {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}

.hero__content.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.hero__badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-xs) var(--spacing-md);
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(79, 70, 229, 0.2);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
  margin-bottom: var(--spacing-xl);
  backdrop-filter: blur(10px);
}

.hero__badge-logo {
  width: 20px;
  height: 20px;
  object-fit: contain;
  flex-shrink: 0;
}

.hero__title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: var(--font-weight-bold);
  line-height: 1.1;
  margin-bottom: var(--spacing-xl);
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.hero__subtitle {
  font-size: clamp(1.125rem, 2vw, 1.375rem);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-3xl);
  max-width: 600px;
}

.hero__actions {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

/* Demo Video */
.hero__visual {
  position: relative;
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s ease-out 0.2s, transform 0.8s ease-out 0.2s;
}

.hero__visual.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.hero__video-wrapper {
  position: relative;
  width: 100%;
  min-height: 320px;
  border-radius: var(--radius-2xl);
  overflow: hidden;
  box-shadow: var(--shadow-2xl);
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
}

.hero__video {
  display: block;
  width: 100%;
  height: auto;
  vertical-align: middle;
}

/* Features Section */
.features {
  padding: var(--spacing-5xl) 0;
  background: var(--color-bg-primary);
}

.features__header {
  text-align: center;
  margin-bottom: var(--spacing-4xl);
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.features__header.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.features__title {
  font-size: clamp(2rem, 4vw, 3.5rem);
  margin-bottom: var(--spacing-lg);
  font-weight: var(--font-weight-bold);
  letter-spacing: -0.02em;
}

.features__subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: var(--color-text-secondary);
  max-width: 600px;
  margin: 0 auto;
  line-height: var(--line-height-relaxed);
}

@media (min-width: 1024px) {
  .features__subtitle {
    max-width: 720px;
  }
}

.features__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-2xl);
}

.feature-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  padding: var(--spacing-3xl);
  text-align: center;
  transition: all var(--transition-base);
  opacity: 0;
  transform: translateY(30px);
}

.feature-card.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.feature-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-card-hover);
  transform: translateY(-4px);
}

.feature-card__icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  background: var(--color-primary-subtle);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
}

.feature-card__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-md);
  color: var(--color-text-primary);
}

.feature-card__description {
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-secondary);
  margin: 0;
}

/* How It Works Section */
.how-it-works {
  padding: var(--spacing-5xl) 0;
  background: var(--color-bg-secondary);
}

.how-it-works__header {
  text-align: center;
  margin-bottom: var(--spacing-3xl);
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.how-it-works__header.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.how-it-works__title {
  font-size: clamp(2rem, 4vw, 3rem);
  margin-bottom: var(--spacing-md);
}

.how-it-works__subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  max-width: 600px;
  margin: 0 auto;
}

@media (min-width: 1024px) {
  .how-it-works__subtitle {
    max-width: 720px;
  }
}

.how-it-works__steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-xl);
}

.step-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl);
  position: relative;
  transition: all var(--transition-base);
  opacity: 0;
  transform: translateY(30px);
}

.step-card.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.step-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
}

.step-card__number {
  width: 48px;
  height: 48px;
  background: var(--color-primary-gradient);
  color: white;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-lg);
}

.step-card__title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-md);
  color: var(--color-text-primary);
}

.step-card__description {
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-secondary);
  margin: 0;
}

/* CTA Section */
.cta {
  padding: var(--spacing-5xl) 0;
  background: var(--color-primary-gradient);
  color: white;
  position: relative;
  overflow: hidden;
}

.cta::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 60%);
  pointer-events: none;
}

.cta__content {
  text-align: center;
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
  position: relative;
  z-index: 1;
}

.cta__content.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.cta__title {
  font-size: clamp(2rem, 4vw, 3.5rem);
  margin-bottom: var(--spacing-lg);
  color: white;
  font-weight: var(--font-weight-bold);
  letter-spacing: -0.02em;
}

.cta__subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  margin-bottom: var(--spacing-3xl);
  opacity: 0.95;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  line-height: var(--line-height-relaxed);
}

/* Responsive */
@media (max-width: 1024px) {
  .hero__container {
    grid-template-columns: 1fr;
    gap: var(--spacing-4xl);
  }
}

@media (max-width: 768px) {
  .hero {
    min-height: auto;
    padding: var(--spacing-2xl) 0 var(--spacing-3xl);
  }

  .hero__badge {
    font-size: var(--font-size-xs);
    padding: var(--spacing-xs) var(--spacing-sm);
  }

  .hero__badge-logo {
    width: 16px;
    height: 16px;
  }

  .hero__title {
    font-size: clamp(2rem, 8vw, 2.5rem);
    margin-bottom: var(--spacing-lg);
  }

  .hero__subtitle {
    font-size: var(--font-size-base);
    margin-bottom: var(--spacing-2xl);
  }

  .hero__actions {
    flex-direction: column;
    gap: var(--spacing-sm);
    width: 100%;
  }

  .hero__video-wrapper {
    border-radius: var(--radius-xl);
  }

  .features {
    padding: var(--spacing-4xl) 0;
  }

  .how-it-works,
  .cta {
    padding: var(--spacing-4xl) 0;
  }

  .features__header,
  .how-it-works__header {
    margin-bottom: var(--spacing-3xl);
  }

  .features__title,
  .how-it-works__title {
    font-size: clamp(1.75rem, 6vw, 2rem);
  }

  .features__subtitle,
  .how-it-works__subtitle {
    font-size: var(--font-size-base);
  }

  .features__grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-xl);
  }

  .how-it-works__steps {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }

  .feature-card {
    padding: var(--spacing-2xl);
  }

  .step-card {
    padding: var(--spacing-lg);
  }

  .cta__title {
    font-size: clamp(1.75rem, 6vw, 2rem);
    margin-bottom: var(--spacing-md);
  }

  .cta__subtitle {
    font-size: var(--font-size-base);
    margin-bottom: var(--spacing-2xl);
  }
}

@media (max-width: 480px) {
  .hero {
    padding: var(--spacing-xl) 0 var(--spacing-2xl);
  }

  .hero__title {
    font-size: clamp(1.75rem, 10vw, 2.25rem);
    line-height: 1.2;
  }

  .hero__subtitle {
    font-size: var(--font-size-sm);
  }

  .hero__video-wrapper {
    border-radius: var(--radius-lg);
  }

  .features,
  .how-it-works,
  .cta {
    padding: var(--spacing-3xl) 0;
  }

  .feature-card {
    padding: var(--spacing-xl);
  }

  .feature-card__icon {
    width: 56px;
    height: 56px;
    margin-bottom: var(--spacing-md);
  }

  .feature-card__icon :deep(svg) {
    width: 28px;
    height: 28px;
  }

  .step-card {
    padding: var(--spacing-md);
  }

  .step-card__number {
    width: 40px;
    height: 40px;
    font-size: var(--font-size-lg);
    margin-bottom: var(--spacing-md);
  }
}
</style>