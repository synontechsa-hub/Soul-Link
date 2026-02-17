-- /backend/app/database/schema.sql
-- /version.py
-- /_dev/

-- ==========================================================
-- SoulLink v1.5.2: Architect - MASTER SCHEMA
-- ==========================================================
-- SoulLink official codenamne: Legion

-- "Does this unit have a soul?"
-- Legion - Mass Effect 2

-- Versioning history and codenames:
-- v1.0.0: Ham Sandwich
-- v1.1.0: Code-kun
-- v1.2.0: I-AM-DATA
-- v1.3.0: Linker
-- v1.4.0: Summoner
-- v1.5.0: Behemoth
-- v1.5.1: Reforged
-- v.1.5.2: Architect

-- 1. USERS & ECONOMY
CREATE TABLE users (
    user_id VARCHAR(12) PRIMARY KEY, 
    username VARCHAR(50) UNIQUE NOT NULL, 
    display_name VARCHAR(100),
    account_tier VARCHAR(20) DEFAULT 'free',
    gems INT DEFAULT 0,
    -- SILENT SYSTEM: Internal 'stamina' for API calls
    -- Not visible to users; triggers ad-flow at 0
    energy INT DEFAULT 100, 
    lifetime_tokens_used BIGINT DEFAULT 0, -- Total tokens consumed
    last_ad_at TIMESTAMP, -- Track last ad trigger to prevent spamming
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. SOULS (High-Fidelity Re-structuring)
CREATE TABLE souls (
    soul_id VARCHAR(50) PRIMARY KEY, -- 'rosalynn'
    name VARCHAR(100) NOT NULL,
    archetype VARCHAR(50),
    gender VARCHAR(20),
    age INT,
    version VARCHAR(20) DEFAULT '1.5.2',
    -- 6 Pillars of the High-Fidelity Schema
    identity_data JSONB NOT NULL DEFAULT '{}',
    appearance_data JSONB NOT NULL DEFAULT '{}',
    personality_data JSONB NOT NULL DEFAULT '{}',
    social_engine JSONB NOT NULL DEFAULT '{}',
    world_presence JSONB NOT NULL DEFAULT '{}',
    system_config JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. LOCATIONS
CREATE TABLE locations (
    location_id VARCHAR(50) PRIMARY KEY, -- 'linkview_cuisine'
    display_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    music_track VARCHAR(100) DEFAULT 'ambient_city_loop.mp3',
    -- 'Judge' and 'Narrator' logic
    system_modifiers JSONB DEFAULT '{}', 
    environmental_prompts JSONB DEFAULT '[]',
    min_intimacy INT DEFAULT 0
);

-- 4. RELATIONSHIPS & STATE
CREATE TABLE user_soul_relationships (
    relationship_id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(12) REFERENCES users(user_id) ON DELETE CASCADE,
    soul_id VARCHAR(50) REFERENCES souls(soul_id) ON DELETE CASCADE,
    intimacy_score INT DEFAULT 0,
    intimacy_tier VARCHAR(20) DEFAULT 'STRANGER', --
    current_location VARCHAR(50) REFERENCES locations(location_id),
    -- Stores curse progress, glove status, etc.
    special_flags JSONB DEFAULT '{}', 
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. CONVERSATIONS
CREATE TABLE conversations (
    msg_id BIGSERIAL PRIMARY KEY,
    relationship_id BIGINT REFERENCES user_soul_relationships(relationship_id),
    role VARCHAR(10) NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    -- Meta-info like tokens used in this specific exchange
    meta_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);