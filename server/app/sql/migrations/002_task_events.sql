-- Task Events (Task Diary) Migration
-- Stores status updates, completion outcomes, and release reasons as an event stream per task.
-- Visible to task owner (who adds them) and plan owner (for follow-up).

-- ============================================================================
-- TASK EVENT TYPES (for reference; enforced in application and CHECK below)
-- ============================================================================
-- status_update : Task owner adds a progress/status note (timestamped).
-- completed      : Task owner marks task complete and provides final outcome.
-- released       : Task owner releases task and provides reason.

-- ============================================================================
-- CARE TASK EVENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.care_task_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    care_task_id UUID NOT NULL REFERENCES public.care_tasks(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL CHECK (event_type IN ('status_update', 'completed', 'released')),
    content TEXT NOT NULL,
    created_by UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_care_task_events_task_id ON public.care_task_events(care_task_id);
CREATE INDEX IF NOT EXISTS idx_care_task_events_created_at ON public.care_task_events(care_task_id, created_at);

COMMENT ON TABLE public.care_task_events IS 'Event diary for tasks: status updates, completion outcomes, release reasons';
