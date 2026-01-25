<template>
  <BaseCard class="care-request-form" variant="elevated">
    <form @submit.prevent="handleSubmit">
      <div class="care-request-form__content">
        <div class="care-request-form__header">
          <h2 class="care-request-form__title">What's going on?</h2>
          <p class="care-request-form__description">
            Describe your situation in your own words. We'll help you figure out the rest.
          </p>
        </div>

        <div class="care-request-form__fields">
          <BaseTextArea
            v-model="formData.narrative"
            placeholder="My mom is recovering from surgery and needs help with meals and getting to appointments for the next few weeks..."
            :rows="4"
            :max-length="VALIDATION.NARRATIVE_MAX_LENGTH"
            :show-char-count="false"
            :auto-resize="true"
            :error="errors.narrative"
            required
          />

          <div class="care-request-form__optional">
            <button
              type="button"
              class="care-request-form__optional-toggle"
              @click="showOptionalFields = !showOptionalFields"
            >
              <span>{{ showOptionalFields ? 'Hide' : 'Add more context' }}</span>
              <BaseIcon 
                :path="mdiChevronDown" 
                :size="16"
                :rotate="showOptionalFields ? 180 : 0"
              />
            </button>

            <Transition name="slide-down">
              <div v-if="showOptionalFields" class="care-request-form__optional-fields">
                <BaseTextArea
                  v-model="formData.constraints"
                  label="Timing & Constraints"
                  placeholder="Any time constraints or scheduling needs? (Optional)"
                  :rows="3"
                  :max-length="VALIDATION.CONSTRAINTS_MAX_LENGTH"
                  :show-char-count="false"
                />

                <BaseTextArea
                  v-model="formData.boundaries"
                  label="Boundaries & Privacy"
                  placeholder="Any privacy concerns or boundaries we should know about? (Optional)"
                  :rows="3"
                  :max-length="VALIDATION.BOUNDARIES_MAX_LENGTH"
                  :show-char-count="false"
                />
              </div>
            </Transition>
          </div>
        </div>

        <div class="care-request-form__actions">
          <BaseButton
            type="submit"
            variant="primary"
            size="lg"
            :loading="isSubmitting"
            :disabled="!isFormValid"
            full-width
          >
            Get Help
          </BaseButton>
          
          <p class="care-request-form__privacy">
            Private and secure. Only shared with people you approve.
          </p>
        </div>
      </div>
    </form>
  </BaseCard>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue';
import BaseCard from '@/components/atoms/BaseCard.vue';
import BaseTextArea from '@/components/atoms/BaseTextArea.vue';
import BaseButton from '@/components/atoms/BaseButton.vue';
import BaseIcon from '@/components/atoms/BaseIcon.vue';
import { VALIDATION } from '@/constants';
import type { CareRequest } from '@/types';
import { mdiChevronDown } from '@mdi/js';

interface FormData {
  narrative: string;
  constraints: string;
  boundaries: string;
}

const emit = defineEmits<{
  submit: [data: Omit<CareRequest, 'id' | 'care_circle_id' | 'status' | 'created_at'>];
}>();

const formData = reactive<FormData>({
  narrative: '',
  constraints: '',
  boundaries: '',
});

const errors = reactive({
  narrative: '',
});

const isSubmitting = ref(false);
const showOptionalFields = ref(false);

const isFormValid = computed(() => {
  return formData.narrative.trim().length >= VALIDATION.NARRATIVE_MIN_LENGTH;
});

const validateForm = (): boolean => {
  errors.narrative = '';
  
  if (!formData.narrative.trim()) {
    errors.narrative = 'Please describe your care situation';
    return false;
  }
  
  if (formData.narrative.trim().length < VALIDATION.NARRATIVE_MIN_LENGTH) {
    errors.narrative = `Please provide more detail (at least ${VALIDATION.NARRATIVE_MIN_LENGTH} characters)`;
    return false;
  }
  
  return true;
};

const handleSubmit = async () => {
  if (!validateForm()) {
    return;
  }

  isSubmitting.value = true;
  
  try {
    const submissionData = {
      narrative: formData.narrative.trim(),
      constraints: formData.constraints.trim() || undefined,
      boundaries: formData.boundaries.trim() || undefined,
    };
    
    emit('submit', submissionData);
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.care-request-form {
  max-width: 680px;
  margin: 0 auto;
  border: none;
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-xl);
  position: relative;
  overflow: hidden;
}

.care-request-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--color-primary-gradient);
}

.care-request-form__content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  padding: var(--spacing-2xl);
}

.care-request-form__header {
  text-align: center;
}

.care-request-form__title {
  font-size: clamp(1.5rem, 4vw, 1.875rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.care-request-form__description {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
  margin: 0;
}

.care-request-form__fields {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.care-request-form__optional {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.care-request-form__optional-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-base);
}

.care-request-form__optional-toggle:hover {
  background: var(--color-bg-secondary);
  border-color: var(--color-primary-light);
  color: var(--color-primary);
}

.care-request-form__optional-toggle svg {
  transition: transform var(--transition-base);
}

.care-request-form__optional-fields {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  padding-top: var(--spacing-xs);
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease-out;
  transform-origin: top;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: scaleY(0.8);
  max-height: 0;
}

.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  transform: scaleY(1);
  max-height: 600px;
}

.care-request-form__actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  align-items: center;
  padding-top: var(--spacing-sm);
}

.care-request-form__privacy {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  text-align: center;
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.care-request-form__privacy::before {
  content: '🔒';
  font-size: var(--font-size-sm);
}

@media (max-width: 640px) {
  .care-request-form__content {
    padding: var(--spacing-xl);
  }

  .care-request-form__title {
    font-size: var(--font-size-xl);
  }

  .care-request-form__description {
    font-size: var(--font-size-xs);
  }
}
</style>
