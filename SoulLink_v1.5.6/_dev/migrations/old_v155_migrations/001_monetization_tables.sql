-- SoulLink v1.5.5: Monetization Tables Migration
-- Run this in Supabase SQL Editor
-- ==========================================
-- TABLE: user_soul_state
-- ==========================================
CREATE TABLE IF NOT EXISTS user_soul_state (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    soul_id VARCHAR(50) NOT NULL,
    signal_stability FLOAT NOT NULL DEFAULT 100.0,
    last_stability_decay TIMESTAMP NOT NULL DEFAULT NOW(),
    nsfw_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    total_messages_sent INTEGER NOT NULL DEFAULT 0,
    total_stability_boosts INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, soul_id)
);
CREATE INDEX IF NOT EXISTS ix_user_soul_state_user_id ON user_soul_state(user_id);
CREATE INDEX IF NOT EXISTS ix_user_soul_state_soul_id ON user_soul_state(soul_id);
-- ==========================================
-- TABLE: ad_impressions
-- ==========================================
CREATE TABLE IF NOT EXISTS ad_impressions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    ad_network VARCHAR(50) NOT NULL,
    ad_type VARCHAR(50) NOT NULL,
    placement VARCHAR(100) NOT NULL,
    reward_granted BOOLEAN NOT NULL DEFAULT FALSE,
    reward_type VARCHAR(50),
    reward_amount FLOAT,
    ssv_verified BOOLEAN NOT NULL DEFAULT FALSE,
    ssv_signature VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_ad_impressions_user_id ON ad_impressions(user_id);
CREATE INDEX IF NOT EXISTS ix_ad_impressions_ad_network ON ad_impressions(ad_network);
CREATE INDEX IF NOT EXISTS ix_ad_impressions_placement ON ad_impressions(placement);
CREATE INDEX IF NOT EXISTS ix_ad_impressions_created_at ON ad_impressions(created_at);
-- ==========================================
-- RLS POLICIES (Row Level Security)
-- ==========================================
-- Enable RLS
ALTER TABLE user_soul_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE ad_impressions ENABLE ROW LEVEL SECURITY;
-- user_soul_state policies
CREATE POLICY "Users can view their own soul states" ON user_soul_state FOR
SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Users can insert their own soul states" ON user_soul_state FOR
INSERT WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "Users can update their own soul states" ON user_soul_state FOR
UPDATE USING (auth.uid()::text = user_id);
-- ad_impressions policies (read-only for users, backend writes via service role)
CREATE POLICY "Users can view their own ad impressions" ON ad_impressions FOR
SELECT USING (auth.uid()::text = user_id);
-- ==========================================
-- VERIFICATION QUERIES
-- ==========================================
-- Run these after migration to verify:
-- SELECT * FROM user_soul_state LIMIT 5;
-- SELECT * FROM ad_impressions LIMIT 5;
-- SELECT COUNT(*) FROM user_soul_state;
-- SELECT COUNT(*) FROM ad_impressions;