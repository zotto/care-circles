/**
 * Core Domain Types
 * Based on Care Circles specification
 */

export interface User {
  id: string;
  email: string;
  role: 'organizer' | 'helper';
}

export interface CareRequest {
  id: string;
  narrative: string;
  constraints?: string;
  boundaries?: string;
  status: 'submitted' | 'processing' | 'completed';
  created_at: string;
}

export interface NeedsMap {
  id: string;
  care_request_id: string;
  summary: string;
  identified_needs: Record<string, any>;
  risks: Record<string, any>;
  assumptions: string;
  created_at: string;
}

export interface CareTask {
  id: string;
  care_request_id: string;
  title: string;
  description: string;
  category: string;
  priority: 'low' | 'medium' | 'high';
  status: 'draft' | 'active' | 'available' | 'claimed' | 'completed';
  created_at: string;
  /** Full name of user who claimed the task (from users table). Shown as "claimed by X" / "completed by X". */
  claimed_by_name?: string;
}

/** Task diary event type */
export type TaskEventType = 'status_update' | 'completed' | 'released' | 'reopened';

export interface CareTaskEvent {
  id: string;
  care_task_id: string;
  event_type: TaskEventType;
  content: string;
  created_by: string;
  created_at: string;
}

export interface ReviewPacket {
  id: string;
  care_request_id: string;
  summary: string;
  draft_tasks: CareTask[];
  agent_notes: string;
  approval_status: 'pending' | 'approved';
  created_at: string;
}

export interface Job {
  id: string;
  care_request_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
}

/**
 * API Request/Response types
 */

export interface CareRequestCreatePayload {
  narrative: string;
  constraints?: string;
  boundaries?: string;
}

export interface CareRequestResponse {
  care_request: CareRequest;
  job_id: string;
}

export interface JobStatusResponse {
  status: string;
  job_id: string;
  care_request_id: string;
  current_agent: string | null;
  agent_progress: Record<string, string>;
  tasks: CareTask[] | null;
  summary?: string | null;
  suggested_plan_name?: string | null;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
}

/**
 * UI-specific types
 */

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface FormFieldError {
  field: string;
  message: string;
}
