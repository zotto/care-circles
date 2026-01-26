-- Care Circles Row Level Security (RLS) Policies
-- Ensures users can only access data they have permission to see

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- ============================================================================
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.care_circles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.care_circle_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.care_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.care_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.care_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.needs_maps ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- HELPER FUNCTIONS FOR RLS POLICIES
-- ============================================================================

-- Check if user is a member of a care circle
CREATE OR REPLACE FUNCTION is_circle_member(circle_id UUID, user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.care_circle_members
        WHERE care_circle_id = circle_id AND user_id = user_id
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user is the owner of a care circle
CREATE OR REPLACE FUNCTION is_circle_owner(circle_id UUID, user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.care_circles
        WHERE id = circle_id AND owner_id = user_id
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Check if user has access to a care request (member or via share token)
CREATE OR REPLACE FUNCTION can_access_care_request(request_id UUID, user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.care_requests cr
        JOIN public.care_circle_members ccm ON ccm.care_circle_id = cr.care_circle_id
        WHERE cr.id = request_id AND ccm.user_id = user_id
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- USERS TABLE POLICIES
-- ============================================================================

-- Users can view their own profile
CREATE POLICY "Users can view own profile"
    ON public.users
    FOR SELECT
    USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON public.users
    FOR UPDATE
    USING (auth.uid() = id);

-- Users can insert their own profile (on signup)
CREATE POLICY "Users can insert own profile"
    ON public.users
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ============================================================================
-- CARE CIRCLES TABLE POLICIES
-- ============================================================================

-- Users can view care circles they are members of
CREATE POLICY "Users can view circles they belong to"
    ON public.care_circles
    FOR SELECT
    USING (
        auth.uid() IN (
            SELECT user_id FROM public.care_circle_members
            WHERE care_circle_id = id
        )
    );

-- Users can create care circles
CREATE POLICY "Users can create care circles"
    ON public.care_circles
    FOR INSERT
    WITH CHECK (auth.uid() = owner_id);

-- Owners can update their care circles
CREATE POLICY "Owners can update their circles"
    ON public.care_circles
    FOR UPDATE
    USING (auth.uid() = owner_id);

-- Owners can delete their care circles
CREATE POLICY "Owners can delete their circles"
    ON public.care_circles
    FOR DELETE
    USING (auth.uid() = owner_id);

-- ============================================================================
-- CARE CIRCLE MEMBERS TABLE POLICIES
-- ============================================================================

-- Members can view other members in their circles
CREATE POLICY "Members can view circle members"
    ON public.care_circle_members
    FOR SELECT
    USING (
        auth.uid() IN (
            SELECT user_id FROM public.care_circle_members m2
            WHERE m2.care_circle_id = care_circle_id
        )
    );

-- Circle owners can add members
CREATE POLICY "Owners can add members"
    ON public.care_circle_members
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.care_circles
            WHERE id = care_circle_id AND owner_id = auth.uid()
        )
    );

-- Circle owners can remove members
CREATE POLICY "Owners can remove members"
    ON public.care_circle_members
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.care_circles
            WHERE id = care_circle_id AND owner_id = auth.uid()
        )
    );

-- ============================================================================
-- CARE REQUESTS TABLE POLICIES
-- ============================================================================

-- Users can view requests in their circles OR via share token
CREATE POLICY "Users can view accessible care requests"
    ON public.care_requests
    FOR SELECT
    USING (
        -- Member of the circle
        auth.uid() IN (
            SELECT user_id FROM public.care_circle_members
            WHERE care_circle_id = care_requests.care_circle_id
        )
        -- Note: Share token access is handled at application level
    );

-- Users can create requests in their circles
CREATE POLICY "Members can create care requests"
    ON public.care_requests
    FOR INSERT
    WITH CHECK (
        auth.uid() IN (
            SELECT user_id FROM public.care_circle_members
            WHERE care_circle_id = care_requests.care_circle_id
        )
        AND auth.uid() = created_by
    );

-- Creators can update their requests
CREATE POLICY "Creators can update their requests"
    ON public.care_requests
    FOR UPDATE
    USING (auth.uid() = created_by);

-- Creators can delete their requests
CREATE POLICY "Creators can delete their requests"
    ON public.care_requests
    FOR DELETE
    USING (auth.uid() = created_by);

-- ============================================================================
-- CARE PLANS TABLE POLICIES
-- ============================================================================

-- Users can view plans in their circles
CREATE POLICY "Users can view accessible care plans"
    ON public.care_plans
    FOR SELECT
    USING (
        auth.uid() IN (
            SELECT user_id FROM public.care_circle_members
            WHERE care_circle_id = care_plans.care_circle_id
        )
    );

-- System can create plans (via service role)
CREATE POLICY "Service can create care plans"
    ON public.care_plans
    FOR INSERT
    WITH CHECK (true);

-- Plan creators can update their plans
CREATE POLICY "Creators can update their plans"
    ON public.care_plans
    FOR UPDATE
    USING (auth.uid() = created_by);

-- ============================================================================
-- CARE TASKS TABLE POLICIES
-- ============================================================================

-- Users can view tasks in accessible plans
CREATE POLICY "Users can view accessible tasks"
    ON public.care_tasks
    FOR SELECT
    USING (
        -- Member of the circle
        auth.uid() IN (
            SELECT user_id FROM public.care_circle_members
            WHERE care_circle_id = care_tasks.care_circle_id
        )
        -- OR task is claimed by user (for cross-circle visibility)
        OR auth.uid() = claimed_by
    );

-- System can create tasks (via service role)
CREATE POLICY "Service can create tasks"
    ON public.care_tasks
    FOR INSERT
    WITH CHECK (true);

-- Task claimers can update their tasks, plan creators can update all
CREATE POLICY "Users can update tasks they own or created"
    ON public.care_tasks
    FOR UPDATE
    USING (
        auth.uid() = claimed_by
        OR auth.uid() IN (
            SELECT created_by FROM public.care_plans
            WHERE id = care_tasks.care_plan_id
        )
    );

-- Plan creators can delete tasks
CREATE POLICY "Plan creators can delete tasks"
    ON public.care_tasks
    FOR DELETE
    USING (
        auth.uid() IN (
            SELECT created_by FROM public.care_plans
            WHERE id = care_tasks.care_plan_id
        )
    );

-- ============================================================================
-- JOBS TABLE POLICIES
-- ============================================================================

-- Users can view jobs for their care requests
CREATE POLICY "Users can view their jobs"
    ON public.jobs
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.care_requests
            WHERE id = jobs.care_request_id
            AND (
                created_by = auth.uid()
                OR care_circle_id IN (
                    SELECT care_circle_id FROM public.care_circle_members
                    WHERE user_id = auth.uid()
                )
            )
        )
    );

-- System can create and update jobs (via service role)
CREATE POLICY "Service can manage jobs"
    ON public.jobs
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- NEEDS MAPS TABLE POLICIES
-- ============================================================================

-- Users can view needs maps for accessible care requests
CREATE POLICY "Users can view accessible needs maps"
    ON public.needs_maps
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.care_requests cr
            JOIN public.care_circle_members ccm ON ccm.care_circle_id = cr.care_circle_id
            WHERE cr.id = needs_maps.care_request_id
            AND ccm.user_id = auth.uid()
        )
    );

-- System can create needs maps (via service role)
CREATE POLICY "Service can create needs maps"
    ON public.needs_maps
    FOR INSERT
    WITH CHECK (true);

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant necessary permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Grant permissions to service role for agent operations
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;
