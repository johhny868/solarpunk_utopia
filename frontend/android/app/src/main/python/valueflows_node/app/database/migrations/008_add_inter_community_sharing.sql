-- Migration 008: Inter-Community Sharing (Peer-to-Peer)
-- Implements individual control over resource visibility across communities
-- Based on: openspec/changes/inter-community-sharing/proposal.md

-- Individual sharing preferences
CREATE TABLE IF NOT EXISTS sharing_preferences (
    user_id TEXT PRIMARY KEY,
    visibility TEXT NOT NULL DEFAULT 'trusted_network' CHECK(visibility IN (
        'my_cell',           -- Only my immediate cell (5-50 people)
        'my_community',      -- My whole community
        'trusted_network',   -- Anyone I trust >= 0.5
        'anyone_local',      -- Anyone within X km
        'network_wide'       -- The whole mesh (trust >= 0.1)
    )),
    location_precision TEXT NOT NULL DEFAULT 'neighborhood' CHECK(location_precision IN (
        'exact',
        'neighborhood',
        'city',
        'region'
    )),
    local_radius_km REAL DEFAULT 25.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sharing_preferences_visibility ON sharing_preferences(visibility);

-- Track cross-community exchanges for metrics only (not for permission)
-- These columns already exist in exchanges table, but adding for clarity:
-- ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS provider_community_id TEXT;
-- ALTER TABLE exchanges ADD COLUMN IF NOT EXISTS receiver_community_id TEXT;

-- Note: provider_community_id and receiver_community_id should be added to exchanges
-- if they don't already exist (they should from GAP-03)
