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
            <BaseIcon :path="mdiHeartCircle" :size="16" />
            <span>AI-Powered Care Coordination</span>
          </div>
          <h1 class="hero__title">
            Transform Caregiving Requests
            <span class="gradient-text">Into Action Plans</span>
          </h1>
          <p class="hero__subtitle">
            Care Circles helps you coordinate care by turning unstructured needs into clear, 
            actionable tasks. Get AI assistance to organize support for those who need it most.
          </p>
          <div class="hero__actions">
            <BaseButton 
              variant="primary" 
              size="lg"
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
              @click="scrollToFeatures"
            >
              Learn More
            </BaseButton>
          </div>
        </div>
        <div 
          class="hero__visual"
          :class="{ 'is-visible': heroVisible }"
        >
          <div ref="card1Ref" class="hero__card hero__card--1">
            <BaseIcon :path="mdiFileDocumentMultiple" :size="32" />
            <div class="hero__card-content">
              <div class="hero__card-title">Care Plans</div>
              <div class="hero__card-subtitle">Organized & Clear</div>
            </div>
          </div>
          <div ref="card2Ref" class="hero__card hero__card--2">
            <BaseIcon :path="mdiAccountMultiple" :size="32" />
            <div class="hero__card-content">
              <div class="hero__card-title">Care Circles</div>
              <div class="hero__card-subtitle">Coordinated Support</div>
            </div>
          </div>
          <div ref="card3Ref" class="hero__card hero__card--3">
            <BaseIcon :path="mdiCheckCircle" :size="32" />
            <div class="hero__card-content">
              <div class="hero__card-title">Tasks</div>
              <div class="hero__card-subtitle">Actionable Steps</div>
            </div>
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
          <h2 class="features__title">Everything You Need</h2>
          <p class="features__subtitle">
            Care Circles brings together AI intelligence and human oversight to create 
            comprehensive care coordination solutions.
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
            Join Care Circles today and experience the future of care coordination
          </p>
          <BaseButton 
            variant="primary" 
            size="lg"
            @click="openLoginModal"
          >
            <template #icon>
              <BaseIcon :path="mdiLogin" :size="20" />
            </template>
            Sign In to Get Started
          </BaseButton>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, type ComponentPublicInstance } from 'vue';
import { useScrollReveal, useStaggeredReveal } from '@/composables/useAnimations';
import { useLoginModal } from '@/composables/useLoginModal';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import {
  mdiHeartCircle,
  mdiLogin,
  mdiFileDocumentMultiple,
  mdiAccountMultiple,
  mdiCheckCircle,
  mdiRobot,
  mdiShieldCheck,
  mdiEyeCheck,
} from '@mdi/js';

const { open: openLoginModal } = useLoginModal();

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

// Card z-index cycling
const card1Ref = ref<HTMLElement | null>(null);
const card2Ref = ref<HTMLElement | null>(null);
const card3Ref = ref<HTMLElement | null>(null);
let zIndexInterval: ReturnType<typeof setInterval> | null = null;
let currentFrontCard = 0;

const cycleCardZIndex = () => {
  const cards = [card1Ref.value, card2Ref.value, card3Ref.value].filter(Boolean) as HTMLElement[];
  if (cards.length !== 3) return;

  // Reset all cards to base state
  cards.forEach((card) => {
    card.style.zIndex = '1';
    card.classList.remove('hero__card--front');
  });

  // Set the front card with a subtle scale effect
  const frontCard = cards[currentFrontCard];
  if (frontCard) {
    frontCard.style.zIndex = '10';
    frontCard.classList.add('hero__card--front');
  }

  // Move to next card
  currentFrontCard = (currentFrontCard + 1) % 3;
};

onMounted(() => {
  // Initialize feature visibility array
  featureVisible.value = new Array(features.length).fill(false);
  stepVisible.value = new Array(steps.length).fill(false);

  // Start z-index cycling after a short delay to ensure cards are rendered
  setTimeout(() => {
    zIndexInterval = setInterval(cycleCardZIndex, 3000); // Cycle every 3 seconds
  }, 500);
});

onUnmounted(() => {
  if (zIndexInterval) {
    clearInterval(zIndexInterval);
  }
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
  padding: var(--spacing-3xl) 0;
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
    radial-gradient(circle at 20% 50%, rgba(79, 70, 229, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(236, 72, 153, 0.1) 0%, transparent 50%);
  background-size: 100% 100%;
}

.hero__container {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-3xl);
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
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(79, 70, 229, 0.2);
  border-radius: var(--radius-full);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
  margin-bottom: var(--spacing-lg);
  backdrop-filter: blur(10px);
}

.hero__title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: var(--font-weight-bold);
  line-height: 1.1;
  margin-bottom: var(--spacing-lg);
  color: var(--color-text-primary);
}

.hero__subtitle {
  font-size: var(--font-size-xl);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-2xl);
  max-width: 600px;
}

@media (min-width: 1024px) {
  .hero__subtitle {
    max-width: 720px;
  }
}

.hero__actions {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.hero__visual {
  position: relative;
  height: 500px;
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.8s ease-out 0.2s, transform 0.8s ease-out 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hero__visual.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.hero__card {
  position: absolute;
  background: white;
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-xl);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: var(--spacing-md);
  border: 1px solid var(--color-border);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform;
  backdrop-filter: blur(10px);
  cursor: default;
  z-index: 1;
}

.hero__card :deep(svg) {
  color: var(--color-primary);
  flex-shrink: 0;
}

.hero__card--front {
  transform: scale(1.05);
  box-shadow: var(--shadow-2xl);
}

.hero__card:hover {
  box-shadow: var(--shadow-2xl);
  z-index: 20 !important;
}

.hero__card--1 {
  top: 40px;
  left: 40px;
  width: 280px;
  animation: floatCard1 6s ease-in-out infinite;
}

.hero__card--1:hover {
  transform: translateY(-8px) scale(1.02);
}

.hero__card--1.hero__card--front {
  transform: scale(1.05);
}

.hero__card--2 {
  top: 160px;
  right: 40px;
  width: 300px;
  animation: floatCard2 6s ease-in-out infinite 2s;
}

.hero__card--2:hover {
  transform: translateY(-8px) scale(1.02);
}

.hero__card--2.hero__card--front {
  transform: scale(1.05);
}

.hero__card--3 {
  bottom: 60px;
  left: 50%;
  width: 260px;
  animation: floatCard3 6s ease-in-out infinite 4s;
  transform: translateX(-50%);
}

.hero__card--3:hover {
  transform: translateX(-50%) translateY(-8px) scale(1.02);
}

.hero__card--3.hero__card--front {
  transform: translateX(-50%) scale(1.05);
}

@keyframes floatCard1 {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-12px);
  }
}

@keyframes floatCard2 {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-12px);
  }
}

@keyframes floatCard3 {
  0%, 100% {
    transform: translateX(-50%) translateY(0px);
  }
  50% {
    transform: translateX(-50%) translateY(-12px);
  }
}

.hero__card-content {
  flex: 1;
  width: 100%;
}

.hero__card-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.hero__card-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

/* Features Section */
.features {
  padding: var(--spacing-3xl) 0;
  background: var(--color-bg-primary);
}

.features__header {
  text-align: center;
  margin-bottom: var(--spacing-3xl);
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.features__header.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.features__title {
  font-size: clamp(2rem, 4vw, 3rem);
  margin-bottom: var(--spacing-md);
}

.features__subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  max-width: 600px;
  margin: 0 auto;
}

@media (min-width: 1024px) {
  .features__subtitle {
    max-width: 720px;
  }
}

.features__grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-xl);
}

.feature-card {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl);
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
  box-shadow: var(--shadow-lg);
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
  padding: var(--spacing-3xl) 0;
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
  padding: var(--spacing-3xl) 0;
  background: var(--color-primary-gradient);
  color: white;
}

.cta__content {
  text-align: center;
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.cta__content.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.cta__title {
  font-size: clamp(2rem, 4vw, 3rem);
  margin-bottom: var(--spacing-md);
  color: white;
}

.cta__subtitle {
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-2xl);
  opacity: 0.9;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

/* Responsive */
@media (max-width: 1024px) {
  .hero__container {
    grid-template-columns: 1fr;
    gap: var(--spacing-2xl);
  }

  .hero__visual {
    height: 400px;
  }

  .hero__card--1 {
    top: 10px;
    left: 10px;
    width: 240px;
  }

  .hero__card--2 {
    top: 120px;
    right: 10px;
    width: 260px;
  }

  .hero__card--3 {
    bottom: 20px;
    left: 50%;
    width: 240px;
  }
}

@media (max-width: 768px) {
  .hero__visual {
    height: 500px;
    min-height: 500px;
  }

  .hero__card--1,
  .hero__card--2,
  .hero__card--3 {
    position: relative;
    top: auto;
    left: auto;
    right: auto;
    bottom: auto;
    transform: none !important;
    width: 100%;
    max-width: 320px;
    margin: 0 auto var(--spacing-md);
    animation: none;
  }

  .hero__card--1:hover,
  .hero__card--2:hover,
  .hero__card--3:hover {
    transform: translateY(-4px) scale(1.01) !important;
  }
}

@media (max-width: 768px) {
  .hero {
    min-height: 80vh;
    padding: var(--spacing-2xl) 0;
  }

  .hero__actions {
    flex-direction: column;
  }

  .hero__actions .button {
    width: 100%;
  }

  .features__grid,
  .how-it-works__steps {
    grid-template-columns: 1fr;
  }
}
</style>