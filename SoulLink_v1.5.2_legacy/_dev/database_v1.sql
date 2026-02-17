-- CORE SOUL DEFINITIONS
CREATE TABLE souls (
    soul_id VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    archetype VARCHAR(50),
    personality_data JSONB, 
    appearance_data JSONB,
    voice_profile JSONB,
    is_active BOOLEAN DEFAULT true
);

-- THE MEMORY SYSTEM
CREATE TABLE memories (
    memory_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    soul_id VARCHAR(50) REFERENCES souls(soul_id),
    memory_content TEXT NOT NULL,
    emotional_weight INT DEFAULT 5,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);