-- Migration 006: Add anonymous gifts support (GAP-61: Emma Goldman)
-- This migration adds the 'anonymous' field to listings table
-- to support anonymous gifts - generosity without attribution

-- Add anonymous column to listings table
ALTER TABLE listings ADD COLUMN anonymous INTEGER DEFAULT 0 NOT NULL;

-- Make agent_id nullable for anonymous gifts
-- SQLite doesn't support ALTER COLUMN, so we work within existing constraints
-- The application layer will handle validation of Optional[str] agent_id

-- Create index for querying anonymous listings efficiently
CREATE INDEX IF NOT EXISTS idx_listings_anonymous
ON listings(anonymous)
WHERE anonymous = 1;

-- Create index for community shelf queries (anonymous offers)
CREATE INDEX IF NOT EXISTS idx_listings_community_shelf
ON listings(listing_type, anonymous, status)
WHERE anonymous = 1 AND listing_type = 'offer' AND status = 'active';
