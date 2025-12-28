-- Migration: Add visibility system for inter-community sharing
-- Date: 2025-12-19
-- Purpose: Enable trust-based visibility control for resources
--
-- Based on: openspec/changes/inter-community-sharing/proposal.md
-- Philosophy: Individual choice, no gatekeepers

-- Create sharing_preferences table
CREATE TABLE IF NOT EXISTS sharing_preferences (
    user_id TEXT PRIMARY KEY,
    visibility TEXT NOT NULL DEFAULT 'trusted_network' CHECK(visibility IN (
        'my_cell',           -- Only immediate cell (5-50 people)
        'my_community',      -- Whole community
        'trusted_network',   -- Anyone with trust >= 0.5
        'anyone_local',      -- Anyone within radius_km
        'network_wide'       -- Anyone with trust >= 0.1
    )),
    location_precision TEXT NOT NULL DEFAULT 'neighborhood' CHECK(location_precision IN (
        'exact', 'neighborhood', 'city', 'region'
    )),
    local_radius_km REAL NOT NULL DEFAULT 25.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Add visibility column to listings (per-resource override)
-- If NULL, use user's sharing preference
ALTER TABLE listings ADD COLUMN visibility TEXT CHECK(visibility IN (
    'my_cell', 'my_community', 'trusted_network', 'anyone_local', 'network_wide'
));

-- Create indexes for efficient filtering
CREATE INDEX IF NOT EXISTS idx_listings_visibility ON listings(visibility);
CREATE INDEX IF NOT EXISTS idx_sharing_prefs_visibility ON sharing_preferences(visibility);

-- Track cross-community exchanges for metrics (not permissions)
ALTER TABLE exchanges ADD COLUMN provider_community_id TEXT;
ALTER TABLE exchanges ADD COLUMN receiver_community_id TEXT;

CREATE INDEX IF NOT EXISTS idx_exchanges_cross_community
ON exchanges(provider_community_id, receiver_community_id)
WHERE provider_community_id IS NOT NULL
  AND receiver_community_id IS NOT NULL;
