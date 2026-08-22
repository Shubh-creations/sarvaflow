-- SarvaFlow Supabase Production Database Schema & Strict RLS Security Policies
-- Compatible with Supabase Postgres 15+

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Create Base Tables
CREATE TABLE IF NOT EXISTS public.invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    tenant_id TEXT NOT NULL DEFAULT 'default-tenant',
    file_name TEXT NOT NULL,
    industry_domain TEXT NOT NULL,
    document_category TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('Confirmed', 'Needs Review', 'Needs Reprocessing')),
    total_amount_usd NUMERIC(15, 2) DEFAULT 0.0,
    overall_confidence NUMERIC(5, 2) DEFAULT 95.0,
    prompt_injection_detected BOOLEAN DEFAULT FALSE,
    raw_payload JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    tenant_id TEXT NOT NULL DEFAULT 'default-tenant',
    action_type TEXT NOT NULL,
    actor_email TEXT NOT NULL,
    approver_email TEXT,
    is_dual_approved BOOLEAN DEFAULT FALSE,
    details JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS public.gst_filings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    tenant_id TEXT NOT NULL DEFAULT 'default-tenant',
    doc_number TEXT NOT NULL,
    supplier_gstin TEXT NOT NULL,
    hsn_sac_code TEXT,
    taxable_amount_inr NUMERIC(15, 2) NOT NULL,
    cgst_amount_inr NUMERIC(15, 2) DEFAULT 0.0,
    sgst_amount_inr NUMERIC(15, 2) DEFAULT 0.0,
    igst_amount_inr NUMERIC(15, 2) DEFAULT 0.0,
    total_amount_inr NUMERIC(15, 2) NOT NULL,
    is_ready_for_filing BOOLEAN DEFAULT FALSE,
    anomalies JSONB DEFAULT '[]'::jsonb
);

-- 3. Safely Add user_id Column to All Tables First
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'invoices' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE public.invoices ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'audit_logs' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE public.audit_logs ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid();
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' AND table_name = 'gst_filings' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE public.gst_filings ADD COLUMN user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE DEFAULT auth.uid();
    END IF;
END $$;

-- 4. Create Performance Indexes
CREATE INDEX IF NOT EXISTS idx_invoices_user_id ON public.invoices(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_gst_filings_user_id ON public.gst_filings(user_id);

-- 5. Role Permissions (Revoke Public Unauthenticated Access)
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.invoices TO authenticated;
GRANT SELECT, INSERT ON public.audit_logs TO authenticated; -- Audit logs are append-only
GRANT SELECT, INSERT, UPDATE, DELETE ON public.gst_filings TO authenticated;

-- 6. Strict Owner-Scoped Row Level Security (RLS) Policies
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.gst_filings ENABLE ROW LEVEL SECURITY;

-- Clean Legacy Policies Idempotently
DROP POLICY IF EXISTS "Allow read for all users" ON public.invoices;
DROP POLICY IF EXISTS "Allow insert for all users" ON public.invoices;
DROP POLICY IF EXISTS "Allow read for authenticated users" ON public.invoices;
DROP POLICY IF EXISTS "Allow insert for authenticated users" ON public.invoices;
DROP POLICY IF EXISTS "Allow read for audit logs" ON public.audit_logs;
DROP POLICY IF EXISTS "Allow insert for audit logs" ON public.audit_logs;
DROP POLICY IF EXISTS "Allow read for gst filings" ON public.gst_filings;
DROP POLICY IF EXISTS "Allow insert for gst filings" ON public.gst_filings;

-- Invoices RLS Policies
DROP POLICY IF EXISTS "Users can view own invoices" ON public.invoices;
CREATE POLICY "Users can view own invoices" ON public.invoices
    FOR SELECT TO authenticated
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own invoices" ON public.invoices;
CREATE POLICY "Users can insert own invoices" ON public.invoices
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own invoices" ON public.invoices;
CREATE POLICY "Users can update own invoices" ON public.invoices
    FOR UPDATE TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can delete own invoices" ON public.invoices;
CREATE POLICY "Users can delete own invoices" ON public.invoices
    FOR DELETE TO authenticated
    USING (auth.uid() = user_id);

-- Audit Logs RLS Policies (Append-only immutable audit trail)
DROP POLICY IF EXISTS "Users can view own audit logs" ON public.audit_logs;
CREATE POLICY "Users can view own audit logs" ON public.audit_logs
    FOR SELECT TO authenticated
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own audit logs" ON public.audit_logs;
CREATE POLICY "Users can insert own audit logs" ON public.audit_logs
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = user_id);

-- GST Filings RLS Policies
DROP POLICY IF EXISTS "Users can view own gst filings" ON public.gst_filings;
CREATE POLICY "Users can view own gst filings" ON public.gst_filings
    FOR SELECT TO authenticated
    USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own gst filings" ON public.gst_filings;
CREATE POLICY "Users can insert own gst filings" ON public.gst_filings
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can update own gst filings" ON public.gst_filings;
CREATE POLICY "Users can update own gst filings" ON public.gst_filings
    FOR UPDATE TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- 7. Enable Supabase Realtime Publication Idempotently
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' AND tablename = 'invoices'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.invoices;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' AND tablename = 'audit_logs'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.audit_logs;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' AND tablename = 'gst_filings'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.gst_filings;
    END IF;
EXCEPTION
    WHEN OTHERS THEN NULL;
END $$;
