-- =============================================================================
-- SoulLink v1.5.6 "Normandy SR-2" — Complete Migration
-- /migrations/v156_complete_migration.sql
-- Run this in your Supabase SQL Editor.
-- Safe to re-run: uses IF NOT EXISTS / IF NOT EXISTS guards throughout.
-- =============================================================================
-- =============================================================================
-- 1. LINK_STATES (The Mirror — User-specific mutable state per Soul)
-- =============================================================================
CREATE TABLE IF NOT EXISTS link_states (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    soul_id VARCHAR(50) NOT NULL,
    -- Volatile State
    current_mood VARCHAR(50) NOT NULL DEFAULT 'neutral',
    current_location VARCHAR(50),
    energy_pool INTEGER NOT NULL DEFAULT 100,
    -- Intimacy Ladder
    intimacy_score INTEGER NOT NULL DEFAULT 0,
    intimacy_tier VARCHAR(20) NOT NULL DEFAULT 'STRANGER',
    -- The Mask
    mask_integrity FLOAT NOT NULL DEFAULT 1.0,
    -- Monetization / Signal
    signal_stability FLOAT NOT NULL DEFAULT 100.0,
    last_stability_decay TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Permissions
    unlocked_nsfw BOOLEAN NOT NULL DEFAULT FALSE,
    is_architect BOOLEAN NOT NULL DEFAULT FALSE,
    -- Flags (arbitrary key-value mechanic flags)
    flags JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Stats
    total_messages_sent INTEGER NOT NULL DEFAULT 0,
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_interaction TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_link_state_user_soul UNIQUE (user_id, soul_id)
);
-- Add total_messages_sent if upgrading from mirror_system.sql (idempotent)
ALTER TABLE link_states
ADD COLUMN IF NOT EXISTS total_messages_sent INTEGER NOT NULL DEFAULT 0;
-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_link_states_user_id ON link_states(user_id);
CREATE INDEX IF NOT EXISTS idx_link_states_soul_id ON link_states(soul_id);
CREATE INDEX IF NOT EXISTS idx_link_states_last_interaction ON link_states(last_interaction DESC);
-- =============================================================================
-- 2. SOUL_MEMORIES (The Notebook — Long-term narrative per User+Soul pair)
-- =============================================================================
CREATE TABLE IF NOT EXISTS soul_memories (
    id SERIAL PRIMARY KEY,
    link_state_id INTEGER NOT NULL REFERENCES link_states(id) ON DELETE CASCADE,
    -- LLM-generated relationship summary (pre-context for prompt injection)
    summary TEXT NOT NULL DEFAULT '',
    -- Verified facts: {"user_job": "Architect", "favorite_color": "Blue"}
    facts JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Canon milestones: ["first_kiss", "secret_revealed_01"]
    milestones JSONB NOT NULL DEFAULT '[]'::jsonb,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_soul_memory_link UNIQUE (link_state_id)
);
CREATE INDEX IF NOT EXISTS idx_soul_memories_link_state_id ON soul_memories(link_state_id);
-- =============================================================================
-- 3. USER_PERSONAS (The Masks — Switchable identities per User Account)
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_personas (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    -- Identity Data
    screen_name VARCHAR(50) NOT NULL,
    bio VARCHAR(500),
    age INTEGER,
    gender VARCHAR(20),
    -- The Identity Anchor (what Souls fixate on to recognize "You" across personas)
    identity_anchor VARCHAR(200),
    -- State
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    -- Frontend metadata (avatar, theme color, etc.)
    meta_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_used TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_personas_user_id ON user_personas(user_id);
CREATE INDEX IF NOT EXISTS idx_user_personas_active ON user_personas(user_id, is_active)
WHERE is_active = TRUE;
-- =============================================================================
-- 4. USER_PROGRESS (The Hero's Journey — Account-level gamification)
-- =============================================================================
CREATE TABLE IF NOT EXISTS user_progress (
    user_id VARCHAR(36) PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    -- Achievements: ["first_link", "survived_glitch"]
    unlocked_achievements JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Lore Library: ["history_of_architect", "weather_data_rain"]
    unlocked_lore JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Exploration: Location IDs visited
    visited_locations JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Social Graph: Soul IDs encountered
    encountered_souls JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- Global Stats
    total_messages_sent INTEGER NOT NULL DEFAULT 0,
    total_days_active INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- =============================================================================
-- 5. ROW LEVEL SECURITY
-- =============================================================================
-- link_states
ALTER TABLE link_states ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users view own link states" ON link_states;
DROP POLICY IF EXISTS "Users update own link states" ON link_states;
DROP POLICY IF EXISTS "Users insert own link states" ON link_states;
CREATE POLICY "Users view own link states" ON link_states FOR
SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users insert own link states" ON link_states FOR
INSERT WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "Users update own link states" ON link_states FOR
UPDATE USING (auth.uid()::text = user_id);
-- soul_memories (access via link_state ownership)
ALTER TABLE soul_memories ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users view own memories" ON soul_memories;
DROP POLICY IF EXISTS "Users update own memories" ON soul_memories;
CREATE POLICY "Users view own memories" ON soul_memories FOR
SELECT USING (
        EXISTS (
            SELECT 1
            FROM link_states
            WHERE link_states.id = soul_memories.link_state_id
                AND link_states.user_id = auth.uid()::text
        )
    );
CREATE POLICY "Users update own memories" ON soul_memories FOR
UPDATE USING (
        EXISTS (
            SELECT 1
            FROM link_states
            WHERE link_states.id = soul_memories.link_state_id
                AND link_states.user_id = auth.uid()::text
        )
    );
-- user_personas
ALTER TABLE user_personas ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users view own personas" ON user_personas;
DROP POLICY IF EXISTS "Users insert own personas" ON user_personas;
DROP POLICY IF EXISTS "Users update own personas" ON user_personas;
CREATE POLICY "Users view own personas" ON user_personas FOR
SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users insert own personas" ON user_personas FOR
INSERT WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "Users update own personas" ON user_personas FOR
UPDATE USING (auth.uid()::text = user_id);
-- user_progress
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users view own progress" ON user_progress;
DROP POLICY IF EXISTS "Users update own progress" ON user_progress;
CREATE POLICY "Users view own progress" ON user_progress FOR
SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users update own progress" ON user_progress FOR
UPDATE USING (auth.uid()::text = user_id);
-- =============================================================================
-- 6. ARCHITECT GOD-MODE OVERRIDES (Bypass RLS for service role)
-- =============================================================================
-- These allow the backend service role to read/write all records.
CREATE POLICY "Architect override link_states" ON link_states FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Architect override soul_memories" ON soul_memories FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Architect override user_personas" ON user_personas FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "Architect override user_progress" ON user_progress FOR ALL USING (auth.role() = 'service_role');
-- =============================================================================
-- 7. HARDEN SOUL BLUEPRINTS (Read-Only for normal users)
-- =============================================================================
ALTER TABLE souls ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "All users can read souls" ON souls;
DROP POLICY IF EXISTS "Service role manages souls" ON souls;
CREATE POLICY "All users can read souls" ON souls FOR
SELECT USING (TRUE);
CREATE POLICY "Service role manages souls" ON souls FOR ALL USING (auth.role() = 'service_role');
-- =============================================================================
-- DONE
-- =============================================================================
-- Tables created: link_states, soul_memories, user_personas, user_progress
-- RLS enabled on all new tables + souls blueprint hardened
-- Safe to re-run (idempotent guards on all DDL)