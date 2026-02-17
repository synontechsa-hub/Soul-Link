-- SoulLink v1.5.6 Migration: User System Split
-- /migrations/user_split.sql
-- Goal: Separate User Account from User Identity
-- 1. Create UserPersonas Table
CREATE TABLE IF NOT EXISTS user_personas (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    -- Identity Data
    screen_name VARCHAR(50) NOT NULL,
    bio VARCHAR(500),
    age INTEGER,
    gender VARCHAR(20),
    identity_anchor VARCHAR(200),
    -- State
    is_active BOOLEAN DEFAULT FALSE,
    last_used TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    meta_data JSONB DEFAULT '{}'::jsonb
);
-- 2. Create UserProgress Table
CREATE TABLE IF NOT EXISTS user_progress (
    user_id VARCHAR(36) PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    -- Gamification
    unlocked_achievements JSONB DEFAULT '[]'::jsonb,
    unlocked_lore JSONB DEFAULT '[]'::jsonb,
    visited_locations JSONB DEFAULT '[]'::jsonb,
    encountered_souls JSONB DEFAULT '[]'::jsonb,
    -- Stats
    total_messages_sent INTEGER DEFAULT 0,
    total_days_active INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc')
);
-- 3. RLS Policies
ALTER TABLE user_personas ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
-- Persona Policies
CREATE POLICY "Users manage their own personas" ON user_personas FOR ALL USING (auth.uid()::text = user_id);
-- Progress Policies
CREATE POLICY "Users view their own progress" ON user_progress FOR
SELECT USING (auth.uid()::text = user_id);
-- 4. Indexing (for Persona Switching speed)
CREATE INDEX idx_user_personas_user_active ON user_personas(user_id, is_active);