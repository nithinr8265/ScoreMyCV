-- ═══════════════════════════════════════════════════════════════
-- ScoreMyCV — Supabase PostgreSQL Schema
-- Run this in your Supabase SQL Editor (Project > SQL Editor > New Query)
-- ═══════════════════════════════════════════════════════════════

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Users ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.users (
  id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name          TEXT NOT NULL,
  email         TEXT UNIQUE NOT NULL,
  password_hash TEXT,
  google_id     TEXT,
  role          TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin')),
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ── Resumes ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.resumes (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  file_name       TEXT,
  file_url        TEXT,
  extracted_text  TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Analyses ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.analyses (
  id                        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id                   UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  resume_id                 UUID REFERENCES public.resumes(id) ON DELETE SET NULL,
  file_name                 TEXT,
  ats_score                 INTEGER CHECK (ats_score BETWEEN 0 AND 100),
  letter_grade              TEXT,
  summary                   TEXT,
  strengths                 JSONB DEFAULT '[]',
  weaknesses                JSONB DEFAULT '[]',
  missing_keywords          JSONB DEFAULT '[]',
  ats_improvements          JSONB DEFAULT '[]',
  formatting_issues         JSONB DEFAULT '[]',
  grammar_issues            JSONB DEFAULT '[]',
  skill_gaps                JSONB DEFAULT '[]',
  recommended_skills        JSONB DEFAULT '[]',
  section_scores            JSONB DEFAULT '{}',
  company_name              TEXT,
  designation               TEXT,
  company_match_percentage  INTEGER,
  company_missing_skills    JSONB DEFAULT '[]',
  company_missing_keywords  JSONB DEFAULT '[]',
  recommended_certifications JSONB DEFAULT '[]',
  suggested_projects        JSONB DEFAULT '[]',
  suggested_resume_changes  JSONB DEFAULT '[]',
  created_at                TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes ─────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_resumes_user_id    ON public.resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user_id   ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created   ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_email        ON public.users(email);

-- ── Storage Bucket ───────────────────────────────────────────────
-- Run this separately in Supabase Storage or via API:
-- INSERT INTO storage.buckets (id, name, public) VALUES ('resumes', 'resumes', false);

-- ── Row Level Security ───────────────────────────────────────────
ALTER TABLE public.users    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.resumes  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;

-- Users: can only read/update own record
CREATE POLICY "users_select_own" ON public.users
  FOR SELECT USING (true);  -- service role reads all; anon reads none

CREATE POLICY "users_update_own" ON public.users
  FOR UPDATE USING (auth.uid()::text = id::text);

-- Resumes: users manage their own
CREATE POLICY "resumes_select_own" ON public.resumes
  FOR SELECT USING (true);

CREATE POLICY "resumes_insert_own" ON public.resumes
  FOR INSERT WITH CHECK (true);

CREATE POLICY "resumes_delete_own" ON public.resumes
  FOR DELETE USING (true);

-- Analyses: users manage their own
CREATE POLICY "analyses_select_own" ON public.analyses
  FOR SELECT USING (true);

CREATE POLICY "analyses_insert_own" ON public.analyses
  FOR INSERT WITH CHECK (true);

CREATE POLICY "analyses_delete_own" ON public.analyses
  FOR DELETE USING (true);

-- ── Helper: promote a user to admin ─────────────────────────────
-- UPDATE public.users SET role = 'admin' WHERE email = 'your@email.com';

-- ═══════════════════════════════════════════════════════════════
-- DONE. Verify tables in Supabase Table Editor.
-- ═══════════════════════════════════════════════════════════════
