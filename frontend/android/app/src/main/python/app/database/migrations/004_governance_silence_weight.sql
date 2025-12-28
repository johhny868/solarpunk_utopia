-- GAP-60: Silence Weight in Governance (bell hooks)
--
-- Tracks participation in decision-making while respecting silence and privacy.
--
-- Privacy Guarantees:
-- 1. Silence is computed (eligible - voted), not stored
-- 2. Outreach records are ephemeral (auto-purge)
-- 3. No tracking of silence patterns over time

CREATE TABLE IF NOT EXISTS vote_sessions (
    id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    cell_id TEXT NOT NULL,
    opened_at TIMESTAMP NOT NULL,
    closes_at TIMESTAMP NOT NULL,
    eligible_voters TEXT NOT NULL,  -- JSON array of user IDs
    votes TEXT NOT NULL DEFAULT '{}',  -- JSON object {user_id: choice}
    extended_count INTEGER DEFAULT 0,
    quorum_required REAL,  -- NULL or 0.0-1.0 for critical decisions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_vote_sessions_cell
    ON vote_sessions(cell_id);

CREATE INDEX IF NOT EXISTS idx_vote_sessions_proposal
    ON vote_sessions(proposal_id);

CREATE INDEX IF NOT EXISTS idx_vote_sessions_closes_at
    ON vote_sessions(closes_at);


-- Ephemeral table - records auto-purged after vote closes
-- This ensures we don't track "who stays silent" over time
CREATE TABLE IF NOT EXISTS vote_outreach (
    id TEXT PRIMARY KEY,
    vote_session_id TEXT NOT NULL,
    sent_at TIMESTAMP NOT NULL,
    sent_to TEXT NOT NULL,  -- JSON array of user IDs
    message TEXT NOT NULL,
    purge_at TIMESTAMP NOT NULL,  -- Set to vote closes_at
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vote_session_id) REFERENCES vote_sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_vote_outreach_purge
    ON vote_outreach(purge_at);

CREATE INDEX IF NOT EXISTS idx_vote_outreach_session
    ON vote_outreach(vote_session_id);

-- Trigger to auto-delete expired outreach records
-- Runs on INSERT to vote_outreach (cleanup old records)
-- Note: Uses datetime() for proper comparison of ISO format timestamps
CREATE TRIGGER IF NOT EXISTS cleanup_expired_outreach
AFTER INSERT ON vote_outreach
BEGIN
    DELETE FROM vote_outreach
    WHERE datetime(replace(purge_at, 'T', ' ')) < datetime('now', 'localtime');
END;

-- Note: We deliberately do NOT create tables to track:
-- - User silence patterns
-- - Individual participation history
-- - Reasons for silence
--
-- bell hooks: Respecting silence IS respecting voice.
