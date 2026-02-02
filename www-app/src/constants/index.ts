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
  STATUS_SCROLL_TOP: 400,
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
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
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

// AI Processing Steps
export const PROCESSING_STEPS = [
  {
    agent: 'A1',
    title: 'Understanding Needs',
    description: 'Analyzing your situation and identifying care requirements',
  },
  {
    agent: 'A2',
    title: 'Generating Tasks',
    description: 'Creating personalized, actionable care tasks',
  },
  {
    agent: 'A3',
    title: 'Quality Review',
    description: 'Ensuring safety and appropriateness',
  },
  {
    agent: 'A4',
    title: 'Optimization',
    description: 'Refining and organizing your care plan',
  },
  {
    agent: 'A5',
    title: 'Final Assembly',
    description: 'Preparing your care plan for review',
  },
] as const;

// Status Values
export const REQUEST_STATUS = ['submitted', 'processing', 'completed'] as const;
export const TASK_STATUS = ['draft', 'active', 'completed'] as const;
export const JOB_STATUS = ['queued', 'running', 'completed', 'failed'] as const;
export const APPROVAL_STATUS = ['pending', 'approved'] as const;

// Care Plan Review (pre-approval validation)
export const CARE_PLAN = {
  /** Default category for manually added tasks */
  DEFAULT_TASK_CATEGORY: 'Other',
  /** Default priority for new empty tasks */
  DEFAULT_TASK_PRIORITY: 'medium' as const,
  /** Validation messages */
  VALIDATION: {
    NO_TASKS: 'Please add at least one task with a title, description, and priority.',
    TASK_MISSING_FIELDS: 'All tasks must have a title, description, and priority. Please complete the highlighted task(s).',
    TASK_MISSING_TITLE: 'Task must have a title.',
    TASK_MISSING_DESCRIPTION: 'Task must have a description.',
    TASK_MISSING_PRIORITY: 'Task must have a priority set.',
  },
} as const;

/** Plan owner actions (edit/delete) copy */
export const PLAN_ACTIONS = {
  EDIT: {
    LABEL: 'Edit',
    SAVE: 'Save',
    CANCEL: 'Cancel',
    SUMMARY_MAX_LENGTH: 200,
    SUCCESS_TITLE: 'Plan updated',
    SUCCESS_MESSAGE: 'Plan name has been updated.',
  },
  DELETE: {
    TITLE: 'Delete plan?',
    MESSAGE: 'This plan and its tasks will be permanently removed. This cannot be undone.',
    CONFIRM: 'Delete',
    CANCEL: 'Cancel',
    SUCCESS_TITLE: 'Plan deleted',
    SUCCESS_MESSAGE: 'The plan has been removed.',
    ERROR_TITLE: 'Failed to delete plan',
  },
} as const;

/** Task diary (My Tasks): add status, complete outcome, release reason */
export const TASK_DIARY = {
  ADD_STATUS: {
    LABEL: 'Add status',
    MESSAGE: 'Your update will be visible to the plan owner.',
    PLACEHOLDER: 'Share progress or a quick update…',
    SUBMIT: 'Save',
    SUCCESS_TITLE: 'Status saved',
    SUCCESS_MESSAGE: 'Your update has been added to the task diary.',
    ERROR_TITLE: 'Failed to add status',
    MAX_LENGTH: 2000,
  },
  COMPLETE: {
    TITLE: 'Mark as complete',
    MESSAGE: 'Add the final outcome so the plan owner can see what was done.',
    OUTCOME_LABEL: 'Final outcome',
    OUTCOME_PLACEHOLDER: 'Describe what was accomplished and any relevant details…',
    CONFIRM: 'Complete',
    CANCEL: 'Cancel',
    ERROR_TITLE: 'Failed to complete task',
    MAX_LENGTH: 2000,
  },
  RELEASE: {
    TITLE: 'Release task',
    MESSAGE: 'Please share why you’re releasing this task so the plan owner is informed.',
    REASON_LABEL: 'Reason for releasing',
    REASON_PLACEHOLDER: 'e.g. schedule change, no longer able to help…',
    CONFIRM: 'Release',
    CANCEL: 'Cancel',
    ERROR_TITLE: 'Failed to release task',
    MAX_LENGTH: 2000,
  },
  REOPEN: {
    TITLE: 'Reopen',
    MESSAGE: 'Provide a reason for reopening so the task owner understands what to address.',
    REASON_LABEL: 'Reason for reopening',
    REASON_PLACEHOLDER: 'e.g. outcome not satisfactory, more details needed…',
    CONFIRM: 'Reopen',
    CANCEL: 'Cancel',
    SUCCESS_TITLE: 'Task reopened',
    SUCCESS_MESSAGE: 'The task has been reopened and re-assigned to the previous owner.',
    ERROR_TITLE: 'Failed to reopen task',
    MAX_LENGTH: 2000,
  },
  DIARY: {
    TITLE: 'Task diary',
    EMPTY: 'No updates yet. Add a status to keep the plan owner in the loop.',
    EVENT_TYPES: {
      status_update: 'Status update',
      completed: 'Completed',
      released: 'Released',
      reopened: 'Reopened',
    } as const,
  },
} as const;

/** Plan approval flow: processing state and success/error copy (single responsibility: UI copy) */
export const PLAN_APPROVAL = {
  PROCESSING: {
    TITLE: 'Approving plan',
    DESCRIPTION: 'Your care plan is being approved. You can continue reviewing while we process.',
  },
  SUCCESS: {
    TITLE: 'Care Plan Approved',
    MESSAGE: 'Your care plan has been successfully approved and is ready to share with your helpers.',
  },
  ERROR: {
    TITLE: 'Failed to Approve Plan',
    MESSAGE: 'Failed to approve plan. Please try again.',
  },
  SHARE: {
    LABEL: 'Share this link with volunteers:',
    COPY_BUTTON: 'Copy',
    COPIED_BUTTON: 'Copied!',
  },
  ACTIONS: {
    DONE: 'Complete',
  },
} as const;
