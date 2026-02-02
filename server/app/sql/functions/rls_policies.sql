-- Row Level Security (RLS) Policies
-- Access is by created_by (care requests, plans) and plan/request ownership.

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- ============================================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.care_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.care_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.care_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.needs_maps ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- USERS TABLE POLICIES
-- ============================================================================
CREATE POLICY "Users can view own profile"
    ON public.users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile"
    ON public.users FOR INSERT WITH CHECK (auth.uid() = id);

-- ============================================================================
-- CARE REQUESTS TABLE POLICIES
-- ============================================================================
CREATE POLICY "Users can view own care requests"
    ON public.care_requests FOR SELECT USING (created_by = auth.uid());
CREATE POLICY "Users can create own care requests"
    ON public.care_requests FOR INSERT WITH CHECK (created_by = auth.uid());
CREATE POLICY "Creators can update their requests"
    ON public.care_requests FOR UPDATE USING (created_by = auth.uid());
CREATE POLICY "Creators can delete their requests"
    ON public.care_requests FOR DELETE USING (created_by = auth.uid());

-- ============================================================================
-- CARE PLANS TABLE POLICIES
-- ============================================================================
CREATE POLICY "Users can view accessible care plans"
    ON public.care_plans FOR SELECT
    USING (
        created_by = auth.uid()
        OR EXISTS (
            SELECT 1 FROM public.care_requests cr
            WHERE cr.id = care_plans.care_request_id AND cr.created_by = auth.uid()
        )
    );
CREATE POLICY "Service can create care plans"
    ON public.care_plans FOR INSERT WITH CHECK (true);
CREATE POLICY "Creators can update their plans"
    ON public.care_plans FOR UPDATE USING (created_by = auth.uid());

-- ============================================================================
-- CARE TASKS TABLE POLICIES
-- ============================================================================
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
CREATE POLICY "Service can create tasks"
    ON public.care_tasks FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update tasks they own or created"
    ON public.care_tasks FOR UPDATE
    USING (
        auth.uid() = claimed_by
        OR auth.uid() IN (
            SELECT created_by FROM public.care_plans WHERE id = care_tasks.care_plan_id
        )
    );
CREATE POLICY "Plan creators can delete tasks"
    ON public.care_tasks FOR DELETE
    USING (
        auth.uid() IN (
            SELECT created_by FROM public.care_plans WHERE id = care_tasks.care_plan_id
        )
    );

-- ============================================================================
-- JOBS TABLE POLICIES
-- ============================================================================
CREATE POLICY "Users can view their jobs"
    ON public.jobs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.care_requests cr
            WHERE cr.id = jobs.care_request_id AND cr.created_by = auth.uid()
        )
    );
CREATE POLICY "Service can manage jobs"
    ON public.jobs FOR ALL USING (true) WITH CHECK (true);

-- ============================================================================
-- NEEDS MAPS TABLE POLICIES
-- ============================================================================
CREATE POLICY "Users can view accessible needs maps"
    ON public.needs_maps FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.care_requests cr
            WHERE cr.id = needs_maps.care_request_id AND cr.created_by = auth.uid()
        )
    );
CREATE POLICY "Service can create needs maps"
    ON public.needs_maps FOR INSERT WITH CHECK (true);

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;
