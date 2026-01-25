import { ref, onMounted, onUnmounted } from 'vue';
import type { Ref } from 'vue';
import { SCROLL } from '@/constants';

interface UseScrollRevealOptions {
  threshold?: number;
  rootMargin?: string;
  once?: boolean;
}

/**
 * Composable for scroll-based reveal animations
 * Elements fade in and slide up when they enter the viewport
 */
export function useScrollReveal(
  options: UseScrollRevealOptions = {}
): {
  isVisible: Ref<boolean>;
  elementRef: Ref<HTMLElement | null>;
} {
  const isVisible = ref(false);
  const elementRef = ref<HTMLElement | null>(null);
  let observer: IntersectionObserver | null = null;

  const { threshold = SCROLL.REVEAL_THRESHOLD, rootMargin = '0px', once = true } = options;

  onMounted(() => {
    if (!elementRef.value) return;

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            isVisible.value = true;
            if (once && observer) {
              observer.disconnect();
            }
          } else if (!once) {
            isVisible.value = false;
          }
        });
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(elementRef.value);
  });

  onUnmounted(() => {
    if (observer) {
      observer.disconnect();
    }
  });

  return {
    isVisible,
    elementRef,
  };
}

/**
 * Composable for scroll progress tracking
 */
export function useScrollProgress(): {
  scrollProgress: Ref<number>;
  scrollY: Ref<number>;
} {
  const scrollProgress = ref(0);
  const scrollY = ref(0);

  const updateScroll = () => {
    scrollY.value = window.scrollY;
    const windowHeight = document.documentElement.scrollHeight - window.innerHeight;
    scrollProgress.value = windowHeight > 0 ? (scrollY.value / windowHeight) * 100 : 0;
  };

  onMounted(() => {
    window.addEventListener('scroll', updateScroll, { passive: true });
    updateScroll();
  });

  onUnmounted(() => {
    window.removeEventListener('scroll', updateScroll);
  });

  return {
    scrollProgress,
    scrollY,
  };
}

/**
 * Composable for parallax scrolling effect
 */
export function useParallax(speed: number = SCROLL.PARALLAX_SPEED): {
  parallaxStyle: Ref<{ transform: string }>;
  parallaxRef: Ref<HTMLElement | null>;
} {
  const parallaxStyle = ref({ transform: 'translateY(0px)' });
  const parallaxRef = ref<HTMLElement | null>(null);

  const updateParallax = () => {
    if (!parallaxRef.value) return;

    const rect = parallaxRef.value.getBoundingClientRect();
    const scrolled = window.scrollY;
    const offset = (scrolled - rect.top) * speed;

    parallaxStyle.value = {
      transform: `translateY(${offset}px)`,
    };
  };

  onMounted(() => {
    window.addEventListener('scroll', updateParallax, { passive: true });
    updateParallax();
  });

  onUnmounted(() => {
    window.removeEventListener('scroll', updateParallax);
  });

  return {
    parallaxStyle,
    parallaxRef,
  };
}

/**
 * Composable for mouse-following effects
 */
export function useMousePosition(): {
  x: Ref<number>;
  y: Ref<number>;
} {
  const x = ref(0);
  const y = ref(0);

  const update = (event: MouseEvent) => {
    x.value = event.clientX;
    y.value = event.clientY;
  };

  onMounted(() => {
    window.addEventListener('mousemove', update, { passive: true });
  });

  onUnmounted(() => {
    window.removeEventListener('mousemove', update);
  });

  return { x, y };
}

/**
 * Composable for staggered animations
 */
export function useStaggeredReveal(
  count: number,
  baseDelay: number = 100
): {
  getDelay: (index: number) => string;
} {
  const getDelay = (index: number): string => {
    return `${index * baseDelay}ms`;
  };

  return { getDelay };
}
