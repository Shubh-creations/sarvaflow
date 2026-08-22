-- SarvaFlow Supabase Production Database Schema & RLS Policies
-- Compatible with Supabase Postgres 15+

-- 1. Enable Required Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Invoices & Document Payloads Table
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

-- 3. Audit Logs & SoD Approvals Table
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

-- 4. GST Filings & Anomaly Audit Table
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

-- 5. Row Level Security (RLS) Policies
ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.gst_filings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow read for authenticated users" ON public.invoices;
CREATE POLICY "Allow read for authenticated users" ON public.invoices FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow insert for authenticated users" ON public.invoices;
CREATE POLICY "Allow insert for authenticated users" ON public.invoices FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Allow read for audit logs" ON public.audit_logs;
CREATE POLICY "Allow read for audit logs" ON public.audit_logs FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow read for gst filings" ON public.gst_filings;
CREATE POLICY "Allow read for gst filings" ON public.gst_filings FOR SELECT USING (true);

-- 6. Enable Supabase Realtime Publication
ALTER PUBLICATION supabase_realtime ADD TABLE public.invoices;
ALTER PUBLICATION supabase_realtime ADD TABLE public.audit_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE public.gst_filings;
