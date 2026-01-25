/**
 * Application Constants
 * Centralized configuration values to avoid magic numbers
 */

// Form Validation
export const VALIDATION = {
  NARRATIVE_MIN_LENGTH: 50,
  NARRATIVE_MAX_LENGTH: 2000,
  CONSTRAINTS_MAX_LENGTH: 1000,
  BOUNDARIES_MAX_LENGTH: 1000,
} as const;

// Animation Timing (milliseconds)
export const ANIMATION = {
  FAST: 150,
  BASE: 200,
  SLOW: 300,
  SLOWER: 500,
  PAGE_TRANSITION: 400,
  SCROLL_REVEAL: 600,
  SUCCESS_DELAY: 100,
} as const;

// Scroll Behavior
export const SCROLL = {
  REVEAL_THRESHOLD: 0.1, // 10% visible
  PARALLAX_SPEED: 0.5,
  SMOOTH_OFFSET: 100,
} as const;

// Layout Breakpoints (pixels)
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  XXL: 1536,
} as const;

// Z-Index Layers
export const Z_INDEX = {
  BASE: 1,
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070,
} as const;

// API Configuration
export const API = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
  POLL_INTERVAL: 2000,
} as const;

// UI Configuration
export const UI = {
  TOAST_DURATION: 5000,
  DEBOUNCE_DELAY: 300,
  THROTTLE_DELAY: 150,
  SKELETON_LINES: 3,
  MAX_MOBILE_WIDTH: 640,
} as const;

// Feature Flags
export const FEATURES = {
  ENABLE_ANALYTICS: false,
  ENABLE_ERROR_REPORTING: false,
  ENABLE_AUTH: false, // Not implemented in v1
  ENABLE_REAL_TIME: false,
} as const;

// Care Task Categories
export const TASK_CATEGORIES = [
  'Transportation',
  'Meals',
  'Medical',
  'Household',
  'Companionship',
  'Administrative',
  'Other',
] as const;

// Care Task Priorities
export const TASK_PRIORITIES = ['low', 'medium', 'high'] as const;

// Status Values
export const REQUEST_STATUS = ['submitted', 'processing', 'completed'] as const;
export const TASK_STATUS = ['draft', 'active', 'completed'] as const;
export const JOB_STATUS = ['queued', 'running', 'completed', 'failed'] as const;
export const APPROVAL_STATUS = ['pending', 'approved'] as const;
