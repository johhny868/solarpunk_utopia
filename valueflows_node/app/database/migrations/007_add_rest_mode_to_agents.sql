-- Migration 007: Add Rest Mode Support (GAP-62: Loafer's Rights)
-- Philosophical foundation: Emma Goldman + Peter Kropotkin
-- "The right to be lazy is sacred"

-- Add status field for rest mode
ALTER TABLE agents ADD COLUMN status TEXT DEFAULT 'active' CHECK(status IN ('active', 'resting', 'sabbatical'));

-- Add note field for context (optional user explanation)
ALTER TABLE agents ADD COLUMN status_note TEXT;

-- Add timestamp for when status was last updated
ALTER TABLE agents ADD COLUMN status_updated_at TEXT;

-- Create index for finding users in rest mode
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);

-- Create index for finding users in rest mode specifically
CREATE INDEX IF NOT EXISTS idx_agents_resting ON agents(status) WHERE status IN ('resting', 'sabbatical');
