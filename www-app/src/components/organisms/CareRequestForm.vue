<template>
  <BaseCard class="care-request-form" variant="elevated">
    <form @submit.prevent="handleSubmit">
      <div class="care-request-form__content">
        <div class="care-request-form__header">
          <h2 class="care-request-form__title">What can we help with?</h2>
          <p class="care-request-form__description">
            Share your caregiving situation with us. Describe what you need help with, 
            any constraints or boundaries, and we'll help coordinate a care plan together.
          </p>
        </div>

        <div class="care-request-form__fields">
          <BaseTextArea
            v-model="formData.narrative"
            label="Your Care Situation"
            placeholder="Tell us about your care situation. For example: My mother is recovering from surgery and needs help with daily activities for the next two weeks. She lives alone and will need assistance with meals, transportation to appointments, and light housekeeping..."
            :rows="8"
            :max-length="VALIDATION.NARRATIVE_MAX_LENGTH"
            :show-char-count="true"
            :auto-resize="true"
            :error="errors.narrative"
            required
            hint="Be as detailed as you'd like. This helps us understand your needs better."
          />

          <div class="care-request-form__optional">
            <button
              type="button"
              class="care-request-form__optional-toggle"
              @click="showOptionalFields = !showOptionalFields"
            >
              <span>{{ showOptionalFields ? 'Hide' : 'Add' }} additional details (optional)</span>
              <BaseIcon 
                :path="mdiChevronDown" 
                :size="16"
                :rotate="showOptionalFields ? 180 : 0"
              />
            </button>

            <div v-if="showOptionalFields" class="care-request-form__optional-fields">
              <BaseTextArea
                v-model="formData.constraints"
                label="Constraints & Timing"
                placeholder="Are there specific time constraints, scheduling needs, or practical limitations we should know about?"
                :rows="4"
                :max-length="VALIDATION.CONSTRAINTS_MAX_LENGTH"
                :show-char-count="true"
                hint="E.g., weekday mornings only, needs to be near a specific location, etc."
              />

              <BaseTextArea
                v-model="formData.boundaries"
                label="Boundaries & Sensitivities"
                placeholder="Are there any boundaries, privacy concerns, or sensitivities we should be mindful of?"
                :rows="4"
                :max-length="VALIDATION.BOUNDARIES_MAX_LENGTH"
                :show-char-count="true"
                hint="This helps us create a respectful and appropriate care plan."
              />
            </div>
          </div>
        </div>

        <div class="care-request-form__info">
          <div class="care-request-form__info-card">
            <BaseIcon :path="mdiInformationOutline" :size="20" />
            <div>
              <strong>What happens next?</strong>
              <p>
                Our AI assistant will analyze your needs and generate a coordinated care plan. 
                You'll have the opportunity to review and approve all tasks before they're shared with helpers.
              </p>
            </div>
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
            Create Care Plan
          </BaseButton>
          
          <p class="care-request-form__privacy">
            Your information is private and will only be shared with approved helpers.
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
import { mdiChevronDown, mdiInformationOutline } from '@mdi/js';

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
  max-width: 800px;
  margin: 0 auto;
  border: none;
  background: var(--color-bg-primary);
  box-shadow: var(--shadow-2xl);
  position: relative;
  overflow: hidden;
}

.care-request-form::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--color-primary-gradient);
}

.care-request-form__content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
}

.care-request-form__header {
  text-align: center;
  position: relative;
}

.care-request-form__title {
  font-size: clamp(1.875rem, 4vw, 2.25rem);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  position: relative;
}

.care-request-form__description {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0;
}

.care-request-form__fields {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.care-request-form__optional {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.care-request-form__optional-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 2px solid var(--color-border-light);
  border-radius: var(--radius-md);
  color: var(--color-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-base);
}

.care-request-form__optional-toggle:hover {
  background: var(--color-primary-subtle);
  border-color: var(--color-primary-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.care-request-form__optional-toggle:active {
  transform: translateY(0);
}

.care-request-form__optional-fields {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  padding-top: var(--spacing-md);
  animation: slideDown 0.4s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    max-height: 1000px;
    transform: translateY(0);
  }
}

.care-request-form__info {
  margin: var(--spacing-lg) 0;
}

.care-request-form__info-card {
  display: flex;
  gap: var(--spacing-lg);
  padding: var(--spacing-xl);
  background: linear-gradient(135deg, var(--color-primary-subtle) 0%, #fdf2f8 100%);
  border-radius: var(--radius-xl);
  border: 2px solid transparent;
  background-clip: padding-box;
  position: relative;
  transition: all var(--transition-base);
}

.care-request-form__info-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-xl);
  padding: 2px;
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-secondary-light) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity var(--transition-base);
}

.care-request-form__info-card:hover::before {
  opacity: 1;
}

.care-request-form__info-card svg {
  flex-shrink: 0;
  color: var(--color-primary);
  margin-top: 4px;
}

.care-request-form__info-card:hover svg {
  transform: scale(1.1);
}

.care-request-form__info-card strong {
  display: block;
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.care-request-form__info-card p {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0;
}

.care-request-form__actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  align-items: center;
  padding-top: var(--spacing-lg);
}

.care-request-form__privacy {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  text-align: center;
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.care-request-form__privacy::before {
  content: '🔒';
  font-size: var(--font-size-base);
}

@media (max-width: 640px) {
  .care-request-form__title {
    font-size: var(--font-size-2xl);
  }

  .care-request-form__description {
    font-size: var(--font-size-base);
  }
  
  .care-request-form__info-card {
    flex-direction: column;
    gap: var(--spacing-md);
  }
}
</style>
