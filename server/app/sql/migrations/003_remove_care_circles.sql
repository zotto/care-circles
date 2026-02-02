-- Remove care circles concept: drop care_circles / care_circle_members and care_circle_id columns.
-- Access is now by created_by (care requests, plans) and plan/request ownership.

-- ============================================================================
-- DROP RLS POLICIES THAT REFERENCE CARE CIRCLES
-- ============================================================================

-- Care requests: drop circle-based policies (we will recreate with created_by)
DROP POLICY IF EXISTS "Users can view accessible care requests" ON public.care_requests;
DROP POLICY IF EXISTS "Members can create care requests" ON public.care_requests;

-- Care plans: drop circle-based policy
DROP POLICY IF EXISTS "Users can view accessible care plans" ON public.care_plans;

-- Care tasks: drop circle-based policy
DROP POLICY IF EXISTS "Users can view accessible tasks" ON public.care_tasks;

-- Jobs: drop circle-based policy
DROP POLICY IF EXISTS "Users can view their jobs" ON public.jobs;

-- Needs maps: drop circle-based policy
DROP POLICY IF EXISTS "Users can view accessible needs maps" ON public.needs_maps;

-- Care circle members and care circles tables
DROP POLICY IF EXISTS "Members can view circle members" ON public.care_circle_members;
DROP POLICY IF EXISTS "Owners can add members" ON public.care_circle_members;
DROP POLICY IF EXISTS "Owners can remove members" ON public.care_circle_members;
DROP POLICY IF EXISTS "Users can view circles they belong to" ON public.care_circles;
DROP POLICY IF EXISTS "Users can create care circles" ON public.care_circles;
DROP POLICY IF EXISTS "Owners can update their circles" ON public.care_circles;
DROP POLICY IF EXISTS "Owners can delete their circles" ON public.care_circles;

-- ============================================================================
-- DROP HELPER FUNCTIONS
-- ============================================================================
DROP FUNCTION IF EXISTS is_circle_member(UUID, UUID);
DROP FUNCTION IF EXISTS is_circle_owner(UUID, UUID);
DROP FUNCTION IF EXISTS can_access_care_request(UUID, UUID);

-- ============================================================================
-- DROP COLUMNS AND INDEXES
-- ============================================================================
ALTER TABLE public.care_requests DROP COLUMN IF EXISTS care_circle_id;
DROP INDEX IF EXISTS public.idx_care_requests_circle_id;

ALTER TABLE public.care_plans DROP COLUMN IF EXISTS care_circle_id;
DROP INDEX IF EXISTS public.idx_care_plans_circle_id;

ALTER TABLE public.care_tasks DROP COLUMN IF EXISTS care_circle_id;
DROP INDEX IF EXISTS public.idx_care_tasks_circle_id;

-- ============================================================================
-- DROP CARE CIRCLE TABLES AND TRIGGER
-- ============================================================================
DROP TRIGGER IF EXISTS update_care_circles_updated_at ON public.care_circles;
DROP TABLE IF EXISTS public.care_circle_members;
DROP TABLE IF EXISTS public.care_circles;

-- ============================================================================
-- NEW RLS POLICIES (created_by / plan ownership)
-- ============================================================================

-- Care requests: user sees and creates their own
CREATE POLICY "Users can view own care requests"
    ON public.care_requests FOR SELECT
    USING (created_by = auth.uid());

CREATE POLICY "Users can create own care requests"
    ON public.care_requests FOR INSERT
    WITH CHECK (created_by = auth.uid());

-- Care plans: user sees plans they created or whose care_request they created
CREATE POLICY "Users can view accessible care plans"
    ON public.care_plans FOR SELECT
    USING (
        created_by = auth.uid()
        OR EXISTS (
            SELECT 1 FROM public.care_requests cr
            WHERE cr.id = care_plans.care_request_id AND cr.created_by = auth.uid()
        )
    );

-- Care tasks: user sees tasks in plans they can see, or tasks they claimed
CREATE POLICY "Users can view accessible care tasks"
    ON public.care_tasks FOR SELECT
    USING (
        claimed_by = auth.uid()
        OR EXISTS (
            SELECT 1 FROM public.care_plans cp
            WHERE cp.id = care_tasks.care_plan_id
            AND (cp.created_by = auth.uid() OR EXISTS (
                SELECT 1 FROM public.care_requests cr
                WHERE cr.id = cp.care_request_id AND cr.created_by = auth.uid()
            ))
        )
    );

-- Jobs: user sees jobs for their care requests
CREATE POLICY "Users can view their jobs"
    ON public.jobs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.care_requests cr
            WHERE cr.id = jobs.care_request_id AND cr.created_by = auth.uid()
        )
    );

-- Needs maps: user sees needs maps for their care requests
CREATE POLICY "Users can view accessible needs maps"
    ON public.needs_maps FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.care_requests cr
            WHERE cr.id = needs_maps.care_request_id AND cr.created_by = auth.uid()
        )
    );
