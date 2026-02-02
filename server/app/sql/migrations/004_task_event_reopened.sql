-- Add 'reopened' event type to task diary (plan owner reopens a completed task with reason).
-- Reopened task is re-assigned to the previous task owner (claimed_by unchanged).

-- ============================================================================
-- CARE TASK EVENTS: ALLOW event_type 'reopened'
-- ============================================================================
ALTER TABLE public.care_task_events
  DROP CONSTRAINT IF EXISTS care_task_events_event_type_check;

ALTER TABLE public.care_task_events
  ADD CONSTRAINT care_task_events_event_type_check
  CHECK (event_type IN ('status_update', 'completed', 'released', 'reopened'));

COMMENT ON TABLE public.care_task_events IS 'Event diary for tasks: status updates, completion outcomes, release reasons, reopen reasons (plan owner)';
