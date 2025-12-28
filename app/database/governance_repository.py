"""
Governance repository - Database operations for silence weight voting.

bell hooks: "To be in the margin is to be part of the whole but outside the main body."
"""

import aiosqlite
import json
from typing import List, Optional
from datetime import datetime

from app.models.governance import (
    VoteSession,
    VoteOutreach,
    VoteChoice
)


class GovernanceRepository:
    """Repository for governance vote sessions with silence tracking"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    async def create_vote_session(self, session: VoteSession) -> VoteSession:
        """Create a new vote session"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO vote_sessions (
                    id, proposal_id, cell_id, opened_at, closes_at,
                    eligible_voters, votes, extended_count, quorum_required, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.id,
                    session.proposal_id,
                    session.cell_id,
                    session.opened_at.isoformat(),
                    session.closes_at.isoformat(),
                    json.dumps(session.eligible_voters),
                    json.dumps({k: v.value for k, v in session.votes.items()}),
                    session.extended_count,
                    session.quorum_required,
                    session.created_at.isoformat()
                )
            )
            await db.commit()

        return session

    async def get_vote_session(self, session_id: str) -> Optional[VoteSession]:
        """Get vote session by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM vote_sessions WHERE id = ?",
                (session_id,)
            )
            row = await cursor.fetchone()

        if not row:
            return None

        return self._row_to_vote_session(row)

    async def cast_vote(
        self,
        session_id: str,
        user_id: str,
        choice: VoteChoice
    ) -> VoteSession:
        """
        Cast a vote in a session.

        Updates the votes JSON object with the user's choice.
        """
        session = await self.get_vote_session(session_id)
        if not session:
            raise ValueError(f"Vote session {session_id} not found")

        if session.is_closed:
            raise ValueError("Voting period has closed")

        if user_id not in session.eligible_voters:
            raise ValueError(f"User {user_id} is not eligible to vote")

        # Update votes dict
        session.votes[user_id] = choice

        # Save to database
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE vote_sessions SET votes = ? WHERE id = ?",
                (json.dumps({k: v.value for k, v in session.votes.items()}), session_id)
            )
            await db.commit()

        return session

    async def extend_vote_session(
        self,
        session_id: str,
        new_closes_at: datetime
    ) -> VoteSession:
        """Extend voting period"""
        session = await self.get_vote_session(session_id)
        if not session:
            raise ValueError(f"Vote session {session_id} not found")

        session.closes_at = new_closes_at
        session.extended_count += 1

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                UPDATE vote_sessions
                SET closes_at = ?, extended_count = ?
                WHERE id = ?
                """,
                (new_closes_at.isoformat(), session.extended_count, session_id)
            )
            await db.commit()

        return session

    async def get_active_sessions(self, cell_id: str) -> List[VoteSession]:
        """Get all active (not yet closed) vote sessions for a cell"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT * FROM vote_sessions
                WHERE cell_id = ? AND closes_at > ?
                ORDER BY closes_at ASC
                """,
                (cell_id, datetime.now().isoformat())
            )
            rows = await cursor.fetchall()

        return [self._row_to_vote_session(row) for row in rows]

    async def get_sessions_by_proposal(self, proposal_id: str) -> List[VoteSession]:
        """Get all vote sessions for a proposal"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM vote_sessions WHERE proposal_id = ?",
                (proposal_id,)
            )
            rows = await cursor.fetchall()

        return [self._row_to_vote_session(row) for row in rows]

    async def create_outreach(self, outreach: VoteOutreach) -> VoteOutreach:
        """
        Create ephemeral outreach record.

        NOTE: This record will be auto-purged when purge_at is reached.
        """
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO vote_outreach (
                    id, vote_session_id, sent_at, sent_to, message, purge_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    outreach.id,
                    outreach.vote_session_id,
                    outreach.sent_at.isoformat(),
                    json.dumps(outreach.sent_to),
                    outreach.message,
                    outreach.purge_at.isoformat(),
                    outreach.created_at.isoformat()
                )
            )
            await db.commit()

        return outreach

    async def get_outreach(self, outreach_id: str) -> Optional[VoteOutreach]:
        """Get outreach record by ID (for testing)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM vote_outreach WHERE id = ?",
                (outreach_id,)
            )
            row = await cursor.fetchone()

        if not row:
            return None

        return self._row_to_outreach(row)

    async def purge_expired_outreach(self, as_of: Optional[datetime] = None) -> int:
        """
        Delete expired outreach records (privacy protection).

        Args:
            as_of: Optional datetime to use for comparison (for testing).
                   Defaults to current time.

        Returns: Number of records deleted
        """
        async with aiosqlite.connect(self.db_path) as db:
            if as_of is not None:
                # Use provided time for comparison (testing)
                cursor = await db.execute(
                    "DELETE FROM vote_outreach WHERE datetime(replace(purge_at, 'T', ' ')) < datetime(?)",
                    (as_of.strftime('%Y-%m-%d %H:%M:%S'),)
                )
            else:
                # Use current local time
                cursor = await db.execute(
                    "DELETE FROM vote_outreach WHERE datetime(replace(purge_at, 'T', ' ')) < datetime('now', 'localtime')"
                )
            await db.commit()
            return cursor.rowcount

    async def get_cell_member_ids(self, cell_id: str) -> List[str]:
        """
        Get list of user IDs who are active members of a cell.

        Args:
            cell_id: ID of the cell

        Returns:
            List of user IDs who are active members
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                """
                SELECT user_id FROM cell_memberships
                WHERE cell_id = ? AND is_active = 1
                ORDER BY joined_at ASC
                """,
                (cell_id,)
            )
            rows = await cursor.fetchall()

        return [row[0] for row in rows]

    def _row_to_vote_session(self, row: aiosqlite.Row) -> VoteSession:
        """Convert database row to VoteSession model"""
        votes_dict = json.loads(row["votes"])
        votes = {k: VoteChoice(v) for k, v in votes_dict.items()}

        return VoteSession(
            id=row["id"],
            proposal_id=row["proposal_id"],
            cell_id=row["cell_id"],
            opened_at=datetime.fromisoformat(row["opened_at"]),
            closes_at=datetime.fromisoformat(row["closes_at"]),
            eligible_voters=json.loads(row["eligible_voters"]),
            votes=votes,
            extended_count=row["extended_count"],
            quorum_required=row["quorum_required"],
            created_at=datetime.fromisoformat(row["created_at"])
        )

    def _row_to_outreach(self, row: aiosqlite.Row) -> VoteOutreach:
        """Convert database row to VoteOutreach model"""
        return VoteOutreach(
            id=row["id"],
            vote_session_id=row["vote_session_id"],
            sent_at=datetime.fromisoformat(row["sent_at"]),
            sent_to=json.loads(row["sent_to"]),
            message=row["message"],
            purge_at=datetime.fromisoformat(row["purge_at"]),
            created_at=datetime.fromisoformat(row["created_at"])
        )
