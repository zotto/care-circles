-- Care Circles Database Schema
-- Initial migration for authentication and persistence

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Extends Supabase auth.users with application-specific profile data
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for email lookups
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- ============================================================================
-- CARE CIRCLES TABLE
-- ============================================================================
-- Represents coordination groups for caregiving
CREATE TABLE IF NOT EXISTS public.care_circles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    owner_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for owner lookups
CREATE INDEX IF NOT EXISTS idx_care_circles_owner_id ON public.care_circles(owner_id);

-- ============================================================================
-- CARE CIRCLE MEMBERS TABLE
-- ============================================================================
-- Many-to-many relationship between users and care circles
CREATE TABLE IF NOT EXISTS public.care_circle_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    care_circle_id UUID NOT NULL REFERENCES public.care_circles(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('owner', 'member')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(care_circle_id, user_id)
);

-- Indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_care_circle_members_circle_id ON public.care_circle_members(care_circle_id);
CREATE INDEX IF NOT EXISTS idx_care_circle_members_user_id ON public.care_circle_members(user_id);

-- ============================================================================
-- CARE REQUESTS TABLE
-- ============================================================================
-- Initial caregiving narratives submitted by organizers
CREATE TABLE IF NOT EXISTS public.care_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    care_circle_id UUID NOT NULL REFERENCES public.care_circles(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    narrative TEXT NOT NULL,
    constraints TEXT,
    boundaries TEXT,
    status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'processing', 'completed')),
    share_token UUID UNIQUE DEFAULT uuid_generate_v4(),
    is_shared BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_care_requests_circle_id ON public.care_requests(care_circle_id);
CREATE INDEX IF NOT EXISTS idx_care_requests_created_by ON public.care_requests(created_by);
CREATE INDEX IF NOT EXISTS idx_care_requests_share_token ON public.care_requests(share_token);
CREATE INDEX IF NOT EXISTS idx_care_requests_status ON public.care_requests(status);

-- ============================================================================
-- CARE PLANS TABLE
-- ============================================================================
-- Generated care plans awaiting approval
CREATE TABLE IF NOT EXISTS public.care_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    care_request_id UUID NOT NULL UNIQUE REFERENCES public.care_requests(id) ON DELETE CASCADE,
    care_circle_id UUID NOT NULL REFERENCES public.care_circles(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'active')),
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_care_plans_request_id ON public.care_plans(care_request_id);
CREATE INDEX IF NOT EXISTS idx_care_plans_circle_id ON public.care_plans(care_circle_id);
CREATE INDEX IF NOT EXISTS idx_care_plans_created_by ON public.care_plans(created_by);
CREATE INDEX IF NOT EXISTS idx_care_plans_status ON public.care_plans(status);

-- ============================================================================
-- CARE TASKS TABLE
-- ============================================================================
-- Actionable units of work for helpers
CREATE TABLE IF NOT EXISTS public.care_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    care_plan_id UUID NOT NULL REFERENCES public.care_plans(id) ON DELETE CASCADE,
    care_request_id UUID NOT NULL REFERENCES public.care_requests(id) ON DELETE CASCADE,
    care_circle_id UUID NOT NULL REFERENCES public.care_circles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'available', 'claimed', 'completed')),
    claimed_by UUID REFERENCES public.users(id) ON DELETE SET NULL,
    claimed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_care_tasks_plan_id ON public.care_tasks(care_plan_id);
CREATE INDEX IF NOT EXISTS idx_care_tasks_request_id ON public.care_tasks(care_request_id);
CREATE INDEX IF NOT EXISTS idx_care_tasks_circle_id ON public.care_tasks(care_circle_id);
CREATE INDEX IF NOT EXISTS idx_care_tasks_status ON public.care_tasks(status);
CREATE INDEX IF NOT EXISTS idx_care_tasks_claimed_by ON public.care_tasks(claimed_by);
CREATE INDEX IF NOT EXISTS idx_care_tasks_priority ON public.care_tasks(priority);

-- ============================================================================
-- JOBS TABLE
-- ============================================================================
-- Tracks background execution of agent pipeline
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    care_request_id UUID NOT NULL REFERENCES public.care_requests(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    current_agent TEXT,
    agent_progress JSONB NOT NULL DEFAULT '{}',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error TEXT,
    result JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_jobs_request_id ON public.jobs(care_request_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);

-- ============================================================================
-- NEEDS MAPS TABLE (Optional - for traceability)
-- ============================================================================
-- Structured interpretation of care requests
CREATE TABLE IF NOT EXISTS public.needs_maps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    care_request_id UUID NOT NULL REFERENCES public.care_requests(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    identified_needs JSONB NOT NULL DEFAULT '{}',
    risks JSONB NOT NULL DEFAULT '{}',
    assumptions TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for request lookups
CREATE INDEX IF NOT EXISTS idx_needs_maps_request_id ON public.needs_maps(care_request_id);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- ============================================================================
-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at column
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_care_circles_updated_at BEFORE UPDATE ON public.care_circles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_care_requests_updated_at BEFORE UPDATE ON public.care_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_care_plans_updated_at BEFORE UPDATE ON public.care_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_care_tasks_updated_at BEFORE UPDATE ON public.care_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================
COMMENT ON TABLE public.users IS 'Application user profiles, extends Supabase auth.users';
COMMENT ON TABLE public.care_circles IS 'Coordination groups for caregiving';
COMMENT ON TABLE public.care_circle_members IS 'Members of care circles with roles';
COMMENT ON TABLE public.care_requests IS 'Initial caregiving narratives submitted by organizers';
COMMENT ON TABLE public.care_plans IS 'Generated care plans awaiting approval';
COMMENT ON TABLE public.care_tasks IS 'Actionable units of work for helpers';
COMMENT ON TABLE public.jobs IS 'Background job execution tracking for agent pipeline';
COMMENT ON TABLE public.needs_maps IS 'Structured needs analysis from care requests';
