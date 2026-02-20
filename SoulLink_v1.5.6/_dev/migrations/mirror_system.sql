-- SoulLink v1.5.6 Migration: The Mirror System
-- /migrations/mirror_system.sql
-- Goal: Separate User State from Soul Blueprints
-- 1. Create LinkState Table (The Mirror)
CREATE TABLE IF NOT EXISTS link_states (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    soul_id VARCHAR(50) NOT NULL,
    -- Volatile State
    current_mood VARCHAR(50) DEFAULT 'neutral',
    current_location VARCHAR(50),
    energy_pool INTEGER DEFAULT 100,
    -- Intimacy
    intimacy_score INTEGER DEFAULT 0,
    intimacy_tier VARCHAR(20) DEFAULT 'STRANGER',
    -- Mask / Persona
    mask_integrity FLOAT DEFAULT 1.0,
    -- Monetization / Stability
    signal_stability FLOAT DEFAULT 100.0,
    last_stability_decay TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    -- Gates
    unlocked_nsfw BOOLEAN DEFAULT FALSE,
    is_architect BOOLEAN DEFAULT FALSE,
    -- Meta
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    last_interaction TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc'),
    flags JSONB DEFAULT '{}'::jsonb,
    -- Constraints
    CONSTRAINT uq_link_state_user_soul UNIQUE (user_id, soul_id)
);
-- 2. Create SoulMemory Table (The Notebook)
CREATE TABLE IF NOT EXISTS soul_memories (
    id SERIAL PRIMARY KEY,
    link_state_id INTEGER NOT NULL REFERENCES link_states(id) ON DELETE CASCADE,
    -- Narrative Data
    summary TEXT DEFAULT '',
    facts JSONB DEFAULT '{}'::jsonb,
    milestones JSONB DEFAULT '[]'::jsonb,
    last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT (now() at time zone 'utc')
);
-- 3. Enable RLS on New Tables
ALTER TABLE link_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE soul_memories ENABLE ROW LEVEL SECURITY;
-- 4. Policies
-- LinkState: Users can only see their own links
CREATE POLICY "Users view own link states" ON link_states FOR
SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users update own link states" ON link_states FOR
UPDATE USING (auth.uid()::text = user_id);
-- SoulMemory: via LinkState ownership
CREATE POLICY "Users view own memories" ON soul_memories FOR
SELECT USING (
        EXISTS (
            SELECT 1
            FROM link_states
            WHERE link_states.id = soul_memories.link_state_id
                AND link_states.user_id = auth.uid()::text
        )
    );