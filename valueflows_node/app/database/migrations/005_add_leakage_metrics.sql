-- Migration 005: Add Leakage Metrics Tables
-- Track counterfactual economic value of gift economy transactions
-- Privacy-preserving aggregates for personal, community, and network impact

PRAGMA foreign_keys = ON;

-- =============================================================================
-- EXCHANGE VALUES
-- =============================================================================
-- Stores the estimated economic value for each exchange
-- Individual values are NEVER publicly visible, only aggregates

CREATE TABLE IF NOT EXISTS exchange_values (
    id TEXT PRIMARY KEY,
    exchange_id TEXT NOT NULL UNIQUE,

    -- Categorization
    category TEXT NOT NULL CHECK(category IN ('food', 'tools', 'transport', 'skills', 'housing', 'goods', 'other')),

    -- Value estimation
    estimated_value REAL NOT NULL,  -- In local currency (USD for now)
    estimation_method TEXT NOT NULL CHECK(estimation_method IN ('market_lookup', 'user_input', 'category_average', 'manual_override')),

    -- User corrections
    user_override REAL,  -- User can correct the valuation
    final_value REAL NOT NULL,  -- Either estimated_value or user_override

    -- Privacy controls
    included_in_aggregates INTEGER NOT NULL DEFAULT 1,  -- User privacy choice (1 = yes, 0 = no)

    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT,

    FOREIGN KEY (exchange_id) REFERENCES exchanges(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_exchange_values_exchange ON exchange_values(exchange_id);
CREATE INDEX IF NOT EXISTS idx_exchange_values_category ON exchange_values(category);
CREATE INDEX IF NOT EXISTS idx_exchange_values_created ON exchange_values(created_at);

-- =============================================================================
-- COMMUNITY METRICS
-- =============================================================================
-- Aggregated metrics by community and time period
-- Rolled up periodically to show community impact

CREATE TABLE IF NOT EXISTS community_metrics (
    id TEXT PRIMARY KEY,
    community_id TEXT NOT NULL,

    -- Time period (supports daily, weekly, monthly)
    period_type TEXT NOT NULL CHECK(period_type IN ('day', 'week', 'month', 'year')),
    period_start TEXT NOT NULL,  -- ISO 8601 date
    period_end TEXT NOT NULL,    -- ISO 8601 date

    -- Aggregated totals
    total_value REAL NOT NULL DEFAULT 0,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    member_count INTEGER NOT NULL DEFAULT 0,  -- Active members in period

    -- Breakdown by category (JSON)
    by_category TEXT,  -- JSON: {"food": 1200.50, "tools": 340.00, ...}

    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT,

    -- Unique constraint on community + period
    UNIQUE(community_id, period_type, period_start)
);

CREATE INDEX IF NOT EXISTS idx_community_metrics_community ON community_metrics(community_id);
CREATE INDEX IF NOT EXISTS idx_community_metrics_period ON community_metrics(period_start);
CREATE INDEX IF NOT EXISTS idx_community_metrics_type ON community_metrics(period_type);

-- =============================================================================
-- PERSONAL METRICS
-- =============================================================================
-- Aggregated metrics by individual user and time period
-- Visible only to the user themselves (privacy-preserving)

CREATE TABLE IF NOT EXISTS personal_metrics (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,

    -- Time period
    period_type TEXT NOT NULL CHECK(period_type IN ('day', 'week', 'month', 'year')),
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,

    -- Aggregated totals
    total_value REAL NOT NULL DEFAULT 0,
    given_value REAL NOT NULL DEFAULT 0,    -- As provider
    received_value REAL NOT NULL DEFAULT 0,  -- As receiver
    transaction_count INTEGER NOT NULL DEFAULT 0,

    -- Breakdown by category (JSON)
    by_category TEXT,

    -- Privacy settings
    show_stats INTEGER NOT NULL DEFAULT 1,  -- User can hide their stats

    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT,

    UNIQUE(agent_id, period_type, period_start),
    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_personal_metrics_agent ON personal_metrics(agent_id);
CREATE INDEX IF NOT EXISTS idx_personal_metrics_period ON personal_metrics(period_start);
CREATE INDEX IF NOT EXISTS idx_personal_metrics_type ON personal_metrics(period_type);

-- =============================================================================
-- NETWORK METRICS
-- =============================================================================
-- Network-wide aggregated metrics
-- Visible to all users to show collective impact

CREATE TABLE IF NOT EXISTS network_metrics (
    id TEXT PRIMARY KEY,

    -- Time period
    period_type TEXT NOT NULL CHECK(period_type IN ('day', 'week', 'month', 'year', 'all_time')),
    period_start TEXT NOT NULL,
    period_end TEXT NOT NULL,

    -- Aggregated totals
    total_value REAL NOT NULL DEFAULT 0,
    transaction_count INTEGER NOT NULL DEFAULT 0,
    active_communities INTEGER NOT NULL DEFAULT 0,
    active_members INTEGER NOT NULL DEFAULT 0,

    -- Breakdown by category (JSON)
    by_category TEXT,

    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT,

    UNIQUE(period_type, period_start)
);

CREATE INDEX IF NOT EXISTS idx_network_metrics_period ON network_metrics(period_start);
CREATE INDEX IF NOT EXISTS idx_network_metrics_type ON network_metrics(period_type);

-- =============================================================================
-- CATEGORY VALUE DEFAULTS
-- =============================================================================
-- Default value estimates for different resource categories
-- Used when no specific market price is available

CREATE TABLE IF NOT EXISTS category_value_defaults (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    subcategory TEXT,

    -- Default values
    default_value REAL NOT NULL,
    unit TEXT NOT NULL,

    -- Context
    description TEXT,
    source TEXT,  -- Where this estimate came from

    -- Metadata
    created_at TEXT NOT NULL,
    updated_at TEXT,

    UNIQUE(category, subcategory)
);

CREATE INDEX IF NOT EXISTS idx_category_defaults_category ON category_value_defaults(category);

-- =============================================================================
-- SEED DEFAULT VALUES
-- =============================================================================
-- Insert some reasonable default values (US dollars)

INSERT OR REPLACE INTO category_value_defaults (id, category, subcategory, default_value, unit, description, source, created_at) VALUES
    ('cat-food-meal', 'food', 'meal', 12.00, 'meal', 'Average home-cooked meal value', 'USDA 2024', datetime('now')),
    ('cat-food-produce', 'food', 'produce', 5.00, 'lb', 'Fresh produce per pound', 'USDA 2024', datetime('now')),
    ('cat-food-bulk', 'food', 'bulk', 3.00, 'lb', 'Bulk grains/beans per pound', 'USDA 2024', datetime('now')),
    ('cat-tools-power', 'tools', 'power_tool', 50.00, 'day', 'Power tool rental per day', 'Home Depot 2024', datetime('now')),
    ('cat-tools-hand', 'tools', 'hand_tool', 15.00, 'day', 'Hand tool rental per day', 'Market average', datetime('now')),
    ('cat-transport-local', 'transport', 'local_ride', 15.00, 'ride', 'Local ride (< 10 miles)', 'Uber/Lyft average', datetime('now')),
    ('cat-transport-long', 'transport', 'long_ride', 35.00, 'ride', 'Long ride (10-30 miles)', 'Uber/Lyft average', datetime('now')),
    ('cat-skills-general', 'skills', 'general', 25.00, 'hour', 'General skilled labor per hour', 'BLS 2024', datetime('now')),
    ('cat-skills-specialized', 'skills', 'specialized', 50.00, 'hour', 'Specialized skills per hour', 'BLS 2024', datetime('now')),
    ('cat-housing-room', 'housing', 'room_night', 75.00, 'night', 'Private room per night', 'Hotel average', datetime('now')),
    ('cat-housing-space', 'housing', 'shared_space', 35.00, 'hour', 'Shared space rental per hour', 'Market average', datetime('now')),
    ('cat-goods-small', 'goods', 'small_item', 20.00, 'item', 'Small household goods', 'Market average', datetime('now')),
    ('cat-goods-large', 'goods', 'large_item', 100.00, 'item', 'Large household goods', 'Market average', datetime('now')),
    ('cat-other', 'other', NULL, 10.00, 'item', 'Miscellaneous items', 'Conservative estimate', datetime('now'));
