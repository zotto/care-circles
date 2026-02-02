<template>
  <div class="text-area">
    <label v-if="label" :for="inputId" class="text-area__label">
      {{ label }}
      <span v-if="required" class="text-area__required">*</span>
    </label>
    
    <div class="text-area__wrapper">
      <textarea
        :id="inputId"
        ref="textareaRef"
        v-model="internalValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :rows="rows"
        :maxlength="maxLength"
        :class="textareaClasses"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${inputId}-error` : undefined"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />
    </div>
    
    <div v-if="showCharCount && maxLength" class="text-area__char-count">
      {{ characterCount }} / {{ maxLength }}
    </div>
    
    <div v-if="hint && !error" class="text-area__hint">
      {{ hint }}
    </div>
    
    <div v-if="error" :id="`${inputId}-error`" class="text-area__error">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';

interface Props {
  modelValue: string;
  label?: string;
  placeholder?: string;
  hint?: string;
  error?: string;
  disabled?: boolean;
  readonly?: boolean;
  required?: boolean;
  rows?: number;
  maxLength?: number;
  showCharCount?: boolean;
  autoResize?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  rows: 4,
  showCharCount: false,
  autoResize: false,
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
  blur: [event: FocusEvent];
  focus: [event: FocusEvent];
}>();

const textareaRef = ref<HTMLTextAreaElement>();
const isFocused = ref(false);
const inputId = `textarea-${Math.random().toString(36).substr(2, 9)}`;

const internalValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

const characterCount = computed(() => props.modelValue.length);

const textareaClasses = computed(() => [
  'text-area__input',
  {
    'text-area__input--error': !!props.error,
    'text-area__input--focused': isFocused.value,
    'text-area__input--disabled': props.disabled,
  },
]);

const handleInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement;
  
  if (props.autoResize) {
    target.style.height = 'auto';
    target.style.height = `${target.scrollHeight}px`;
  }
};

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false;
  emit('blur', event);
};

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true;
  emit('focus', event);
};

watch(
  () => props.modelValue,
  () => {
    if (props.autoResize && textareaRef.value) {
      textareaRef.value.style.height = 'auto';
      textareaRef.value.style.height = `${textareaRef.value.scrollHeight}px`;
    }
  }
);
</script>

<style scoped>
.text-area {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.text-area__label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  display: block;
}

.text-area__required {
  color: var(--color-error);
  margin-left: var(--spacing-xs);
}

.text-area__wrapper {
  position: relative;
}

.text-area__input {
  width: 100%;
  padding: var(--spacing-lg);
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  color: var(--color-text-primary);
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-input);
  resize: vertical;
  transition: all var(--transition-fast);
  min-height: 120px;
}

.text-area__input::placeholder {
  color: var(--color-text-tertiary);
}

.text-area__input:hover:not(:disabled):not(:readonly) {
  border-color: var(--color-primary);
  background-color: var(--color-bg-primary);
}

.text-area__input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
  background-color: var(--color-bg-primary);
}

.text-area__input--error {
  border-color: var(--color-error);
}

.text-area__input--error:focus {
  box-shadow: 0 0 0 3px var(--color-error-light);
}

.text-area__input--disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--color-bg-tertiary);
}

.text-area__char-count {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  text-align: right;
}

.text-area__hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.text-area__error {
  font-size: var(--font-size-sm);
  color: var(--color-error);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}
</style>
