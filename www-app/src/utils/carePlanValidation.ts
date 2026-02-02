/**
 * Care plan validation utilities.
 * Single responsibility: validate tasks before plan approval.
 */

import type { CareTask } from '@/types';
import { CARE_PLAN } from '@/constants';

/** Task-like shape for validation (subset of CareTask) */
export interface TaskForValidation {
  title: string;
  description: string;
  priority?: string;
}

export interface CarePlanValidationResult {
  valid: boolean;
  message?: string;
  /** 1-based task numbers that are invalid (for user-facing messages) */
  invalidTaskNumbers?: number[];
}

/**
 * Returns true if the task is considered empty (no title and no description).
 * Empty tasks are excluded from approval and validation.
 */
export function isTaskEmpty(task: TaskForValidation): boolean {
  const title = (task.title ?? '').trim();
  const description = (task.description ?? '').trim();
  return title === '' && description === '';
}

/**
 * Returns only non-empty tasks (tasks that have at least title or description).
 */
export function getNonEmptyTasks(tasks: TaskForValidation[]): TaskForValidation[] {
  return tasks.filter((t) => !isTaskEmpty(t));
}

/**
 * Validates that all non-empty tasks have title, description, and priority.
 * Empty tasks are ignored. Returns validation result with message and invalid task numbers if invalid.
 */
export function validateTasksForApproval(tasks: TaskForValidation[]): CarePlanValidationResult {
  const nonEmpty = getNonEmptyTasks(tasks);
  if (nonEmpty.length === 0) {
    return {
      valid: false,
      message: CARE_PLAN.VALIDATION.NO_TASKS,
    };
  }

  const invalidTaskNumbers: number[] = [];
  tasks.forEach((task, index) => {
    if (isTaskEmpty(task)) return;
    const title = (task.title ?? '').trim();
    const description = (task.description ?? '').trim();
    const priority = task.priority?.trim();
    const hasPriority =
      priority === 'low' || priority === 'medium' || priority === 'high';
    if (title === '' || description === '' || !hasPriority) {
      invalidTaskNumbers.push(index + 1);
    }
  });

  if (invalidTaskNumbers.length > 0) {
    return {
      valid: false,
      message: CARE_PLAN.VALIDATION.TASK_MISSING_FIELDS,
      invalidTaskNumbers,
    };
  }

  return { valid: true };
}

/**
 * Returns only tasks that are non-empty and fully valid (title, description, priority).
 * Use this to build the list to send to the API on approve.
 */
export function getValidTasksForSubmit(tasks: CareTask[]): CareTask[] {
  return tasks.filter((task) => {
    if (isTaskEmpty(task)) return false;
    const title = (task.title ?? '').trim();
    const description = (task.description ?? '').trim();
    const priority = task.priority?.trim();
    const hasPriority =
      priority === 'low' || priority === 'medium' || priority === 'high';
    return title !== '' && description !== '' && hasPriority;
  });
}
