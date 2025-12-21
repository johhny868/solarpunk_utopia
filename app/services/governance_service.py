"""
Governance service - Business logic for silence weight voting.

bell hooks: "I will not have my life narrowed down. I will not bow down to
somebody else's whim or to someone else's ignorance."

Respecting silence IS respecting voice.
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from app.database.governance_repository import GovernanceRepository
from app.models.governance import (
    VoteSession,
    VoteOutreach,
    VoteChoice,
    SilenceMetrics
)


class GovernanceService:
    """Service for managing governance votes with silence awareness"""

    def __init__(self, repo: GovernanceRepository):
        self.repo = repo

    async def create_vote(
        self,
        proposal_id: str,
        cell_id: str,
        duration_hours: int = 72,
        quorum_required: Optional[float] = None
    ) -> VoteSession:
        """
        Create a new vote session.

        Args:
            proposal_id: ID of the proposal being voted on
            cell_id: ID of the cell voting
            duration_hours: How long the vote stays open (default: 3 days)
            quorum_required: Minimum participation rate (0.0-1.0) for critical votes

        Returns:
            Created vote session
        """
        # Get current cell members as eligible voters
        # TODO: This should query the cells/members system
        # For now, we'll require eligible_voters to be passed in or use a default
        eligible_voters = await self._get_cell_members(cell_id)

        session = VoteSession(
            id=str(uuid.uuid4()),
            proposal_id=proposal_id,
            cell_id=cell_id,
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=duration_hours),
            eligible_voters=eligible_voters,
            votes={},
            extended_count=0,
            quorum_required=quorum_required
        )

        return await self.repo.create_vote_session(session)

    async def cast_vote(
        self,
        session_id: str,
        user_id: str,
        choice: VoteChoice
    ) -> VoteSession:
        """
        Cast a vote.

        Args:
            session_id: ID of the vote session
            user_id: ID of the user voting
            choice: yes/no/abstain

        Returns:
            Updated vote session

        Raises:
            ValueError: If session not found, closed, or user not eligible
        """
        return await self.repo.cast_vote(session_id, user_id, choice)

    async def check_silence_weight(self, session_id: str) -> SilenceMetrics:
        """
        Get silence and participation metrics for display.

        These are computed on-the-fly, not stored.

        Returns:
            Silence metrics with gentle prompt if needed
        """
        session = await self.repo.get_vote_session(session_id)
        if not session:
            raise ValueError("Session not found")

        metrics = SilenceMetrics(
            silence_weight=session.silence_weight,
            participation_rate=session.participation_rate,
            should_pause=session.should_pause,
            has_quorum=session.has_quorum,
            silent_count=len(session.silent_voters),
            voted_count=len(session.votes),
            eligible_count=len(session.eligible_voters)
        )

        # Add gentle prompt if silence is high
        if session.silence_weight > 0.5:
            metrics.prompt = (
                f"{metrics.silent_count} people haven't voted yet. "
                "More people are silent than voted. What does this mean?"
            )
        elif session.silence_weight > 0.3:
            metrics.prompt = (
                f"{metrics.silent_count} people haven't voted yet. "
                "Consider reaching out gently."
            )

        return metrics

    async def send_gentle_check_in(
        self,
        session_id: str,
        moderator_id: str
    ) -> VoteOutreach:
        """
        Send a gentle check-in to silent voters.

        bell hooks: No shaming, no pressure. Just awareness.

        Args:
            session_id: ID of the vote session
            moderator_id: ID of the moderator sending the check-in

        Returns:
            Ephemeral outreach record (will be auto-purged)

        Note:
            - Message is gentle, not demanding
            - No tracking of who responds or why
            - Record is ephemeral (deleted when vote closes)
        """
        session = await self.repo.get_vote_session(session_id)
        if not session:
            raise ValueError("Session not found")

        if not session.silent_voters:
            raise ValueError("No silent voters to notify")

        # Create non-shaming message
        message = (
            f"We're voting on a proposal. No pressure to vote, but wanted you to know. "
            f"Closes {session.closes_at.strftime('%b %d at %I:%M%p')}. "
            f"Your voice matters, and so does your silence."
        )

        outreach = VoteOutreach(
            id=str(uuid.uuid4()),
            vote_session_id=session_id,
            sent_at=datetime.now(),
            sent_to=session.silent_voters,
            message=message,
            purge_at=session.closes_at  # Auto-purge when vote closes
        )

        # Save ephemeral record
        await self.repo.create_outreach(outreach)

        # TODO: Send actual notifications via notification system
        # await self.notification_service.send_batch(
        #     user_ids=outreach.sent_to,
        #     message=outreach.message,
        #     type="gentle_reminder"
        # )

        return outreach

    async def extend_vote_session(
        self,
        session_id: str,
        additional_hours: int
    ) -> VoteSession:
        """
        Extend voting period (useful for low participation).

        Args:
            session_id: ID of the vote session
            additional_hours: Hours to extend

        Returns:
            Updated vote session
        """
        session = await self.repo.get_vote_session(session_id)
        if not session:
            raise ValueError("Session not found")

        new_closes_at = session.closes_at + timedelta(hours=additional_hours)
        return await self.repo.extend_vote_session(session_id, new_closes_at)

    async def get_active_sessions(self, cell_id: str) -> List[VoteSession]:
        """Get all active vote sessions for a cell"""
        return await self.repo.get_active_sessions(cell_id)

    async def get_session(self, session_id: str) -> Optional[VoteSession]:
        """Get a specific vote session"""
        return await self.repo.get_vote_session(session_id)

    async def purge_expired_outreach(self) -> int:
        """
        Delete expired outreach records (privacy protection).

        This should be called periodically by a background job.

        Returns:
            Number of records deleted
        """
        return await self.repo.purge_expired_outreach()

    # Helper methods

    async def _get_cell_members(self, cell_id: str) -> List[str]:
        """
        Get list of user IDs who are members of the cell.
        """
        # Query actual cell memberships from database
        members = await self.repo.get_cell_member_ids(cell_id)
        return members

    def _generate_id(self) -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())


# Dependency injection helper
def get_governance_service(db_path: str = "app/data/commune.db") -> GovernanceService:
    """Get governance service instance"""
    repo = GovernanceRepository(db_path)
    return GovernanceService(repo)
