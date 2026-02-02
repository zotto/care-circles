<template>
  <input
    :id="inputId"
    v-model="internalValue"
    :type="type"
    :placeholder="placeholder"
    :disabled="disabled"
    :readonly="readonly"
    :maxlength="maxLength"
    :class="inputClasses"
    :aria-invalid="!!error"
    :aria-describedby="error ? `${inputId}-error` : undefined"
    @blur="handleBlur"
    @focus="handleFocus"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  modelValue: string;
  type?: 'text' | 'email' | 'password' | 'tel' | 'url';
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  readonly?: boolean;
  maxLength?: number;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
  blur: [event: FocusEvent];
  focus: [event: FocusEvent];
}>();

const isFocused = ref(false);
const inputId = `input-${Math.random().toString(36).substr(2, 9)}`;

const internalValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});

const inputClasses = computed(() => [
  'base-input',
  {
    'base-input--error': !!props.error,
    'base-input--focused': isFocused.value,
    'base-input--disabled': props.disabled,
  },
]);

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false;
  emit('blur', event);
};

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true;
  emit('focus', event);
};
</script>

<style scoped>
.base-input {
  width: 100%;
  height: var(--height-input-md);
  padding: 0 var(--spacing-lg);
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  color: var(--color-text-primary);
  background-color: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-input);
  transition: all var(--transition-fast);
}

.base-input::placeholder {
  color: var(--color-text-tertiary);
}

.base-input:hover:not(:disabled):not(:readonly) {
  border-color: var(--color-primary);
  background-color: var(--color-bg-primary);
}

.base-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-subtle);
  background-color: var(--color-bg-primary);
}

.base-input--error {
  border-color: var(--color-error);
}

.base-input--error:focus {
  box-shadow: 0 0 0 3px var(--color-error-light);
}

.base-input--disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background-color: var(--color-bg-tertiary);
}
</style>
