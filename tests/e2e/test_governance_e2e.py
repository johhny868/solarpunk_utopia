"""
End-to-End tests for Governance Silence Weight system (GAP-60).

Tests the complete flow from vote creation through to completion.

bell hooks: "The function of art is to do more than tell it like it is -
it's to imagine what is possible."
"""

import pytest
import pytest_asyncio
import asyncio
import os
import tempfile
from datetime import datetime, timedelta
from freezegun import freeze_time

from app.models.governance import VoteChoice, CreateVoteRequest
from app.database.governance_repository import GovernanceRepository
from app.services.governance_service import GovernanceService


class TestGovernanceE2E:
    """End-to-end governance flow tests"""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Set up test database and service (pytest-asyncio fixture)"""
        # Setup
        # Create temp database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")

        # Run migration
        import aiosqlite
        async with aiosqlite.connect(self.db_path) as db:
            with open("app/database/migrations/004_governance_silence_weight.sql") as f:
                migration_sql = f.read()
            await db.executescript(migration_sql)
            await db.commit()

        # Create repository and service
        self.repo = GovernanceRepository(self.db_path)
        self.service = GovernanceService(self.repo)

        # Mock cell members
        self.service._get_cell_members = self._mock_get_cell_members

        yield  # Run the test

        # Teardown
        os.close(self.db_fd)
        os.unlink(self.db_path)

    async def _mock_get_cell_members(self, cell_id: str):
        """Mock cell membership for testing"""
        return {
            "sunrise-collective": ["alice", "bob", "carol", "dave", "eve",
                                    "frank", "grace", "hank", "iris", "jack"]
        }.get(cell_id, [])

    @pytest.mark.asyncio
    async def test_full_vote_flow_with_silence_check(self):
        """
        E2E test - create vote, cast votes, check silence, extend, close

        Complete flow: create vote → cast votes → check silence → extend → close

        Scenario:
        - 10 eligible voters
        - 3 vote initially (70% silent)
        - System shows silence_weight and suggests pause
        - Moderator sends check-in
        - Vote extended
        - More people vote
        - Quorum reached
        """

        # Step 1: Create vote session (quorum = 50%)
        session = await self.service.create_vote(
            proposal_id="prop-mutual-aid",
            cell_id="sunrise-collective",
            duration_hours=24,
            quorum_required=0.5  # Need 50% participation
        )

        assert session.id is not None
        assert len(session.eligible_voters) == 10
        assert len(session.votes) == 0
        assert session.silence_weight == pytest.approx(1.0)

        # Step 2: Three people vote (30% participation)
        await self.service.cast_vote(session.id, "alice", VoteChoice.YES)
        await self.service.cast_vote(session.id, "bob", VoteChoice.YES)
        await self.service.cast_vote(session.id, "carol", VoteChoice.NO)

        # Step 3: Check silence metrics
        metrics = await self.service.check_silence_weight(session.id)

        assert metrics.silence_weight == pytest.approx(0.7)  # 7 silent out of 10
        assert metrics.participation_rate == pytest.approx(0.3)
        assert metrics.should_pause == True  # More silent than voted
        assert metrics.has_quorum == False  # Below 50% quorum
        assert metrics.prompt is not None  # Should suggest action
        assert "7 people" in metrics.prompt

        # Step 4: Send gentle check-in to silent voters
        outreach = await self.service.send_gentle_check_in(
            session_id=session.id,
            moderator_id="facilitator"
        )

        assert len(outreach.sent_to) == 7  # 7 silent voters
        assert "No pressure" in outreach.message  # Gentle, not shaming
        assert outreach.purge_at == session.closes_at  # Will be purged

        # Step 5: Extend vote by 48 hours
        extended_session = await self.service.extend_vote_session(
            session_id=session.id,
            additional_hours=48
        )

        assert extended_session.extended_count == 1
        assert extended_session.closes_at > session.closes_at

        # Step 6: Two more people vote after extension
        await self.service.cast_vote(session.id, "dave", VoteChoice.YES)
        await self.service.cast_vote(session.id, "eve", VoteChoice.ABSTAIN)

        # Step 7: Check metrics again
        metrics = await self.service.check_silence_weight(session.id)

        assert metrics.participation_rate == pytest.approx(0.5)  # 5 out of 10
        assert metrics.has_quorum == True  # Met 50% quorum!
        assert metrics.should_pause == False  # Equal split (5 vs 5), not "more" silent

        # Step 8: One more vote tips the balance
        await self.service.cast_vote(session.id, "frank", VoteChoice.YES)

        metrics = await self.service.check_silence_weight(session.id)
        assert metrics.should_pause == False  # Now 6 voted > 4 silent

        # Step 9: Fast-forward to after vote closes
        with freeze_time(extended_session.closes_at + timedelta(hours=1)):
            final_session = await self.service.get_session(session.id)

            assert final_session.is_closed == True
            assert final_session.result == "passed"  # 4 yes, 1 no, 1 abstain
            assert final_session.has_quorum == True

            # Step 10: Outreach record should be purged
            purged = await self.service.purge_expired_outreach()
            assert purged >= 1  # At least our outreach

            retrieved_outreach = await self.repo.get_outreach(outreach.id)
            assert retrieved_outreach is None  # Purged for privacy

    @pytest.mark.asyncio
    async def test_critical_vote_requires_quorum(self):
        """
        Critical decisions need high quorum.

        Scenario:
        - Vote requires 80% quorum
        - Only 60% participate
        - Vote fails with no_quorum result
        """

        # Create vote with high quorum requirement
        session = await self.service.create_vote(
            proposal_id="prop-critical-decision",
            cell_id="sunrise-collective",
            duration_hours=72,
            quorum_required=0.8  # Need 80% participation
        )

        # 6 out of 10 vote (60% participation)
        for user in ["alice", "bob", "carol", "dave", "eve", "frank"]:
            await self.service.cast_vote(session.id, user, VoteChoice.YES)

        metrics = await self.service.check_silence_weight(session.id)

        assert metrics.participation_rate == pytest.approx(0.6)  # 60%
        assert metrics.has_quorum == False  # Below 80% requirement
        assert metrics.silent_count == 4  # 4 people silent

        # Fast-forward to close
        with freeze_time(session.closes_at + timedelta(hours=1)):
            final_session = await self.service.get_session(session.id)

            assert final_session.result == "no_quorum"  # Failed due to quorum

    @pytest.mark.asyncio
    async def test_no_shaming_when_all_silent(self):
        """
        When everyone is silent, system respects that.

        Scenario:
        - Vote created
        - No one votes
        - Metrics show 100% silence
        - Can't send check-in if no one has shown interest
        """

        session = await self.service.create_vote(
            proposal_id="prop-ignored",
            cell_id="sunrise-collective",
            duration_hours=24
        )

        # No one votes
        metrics = await self.service.check_silence_weight(session.id)

        assert metrics.silence_weight == pytest.approx(1.0)
        assert metrics.silent_count == 10
        assert metrics.should_pause == True

        # Can send check-in (since there are silent voters)
        outreach = await self.service.send_gentle_check_in(
            session_id=session.id,
            moderator_id="facilitator"
        )

        assert len(outreach.sent_to) == 10
        assert "Your voice matters, and so does your silence" in outreach.message

    @pytest.mark.asyncio
    async def test_abstain_counts_as_participation(self):
        """
        Abstaining is a valid choice and counts toward quorum.

        bell hooks: Choosing not to choose is still a choice.
        """

        session = await self.service.create_vote(
            proposal_id="prop-abstain-test",
            cell_id="sunrise-collective",
            duration_hours=24,
            quorum_required=0.5
        )

        # 5 people abstain (valid participation)
        for user in ["alice", "bob", "carol", "dave", "eve"]:
            await self.service.cast_vote(session.id, user, VoteChoice.ABSTAIN)

        metrics = await self.service.check_silence_weight(session.id)

        assert metrics.participation_rate == pytest.approx(0.5)  # 50% participated
        assert metrics.has_quorum == True  # Abstains count!

    @pytest.mark.asyncio
    async def test_vote_extension_multiple_times(self):
        """Can extend vote multiple times for persistent low turnout"""

        session = await self.service.create_vote(
            proposal_id="prop-slow-response",
            cell_id="sunrise-collective",
            duration_hours=24
        )

        original_closes = session.closes_at

        # Extend once
        session = await self.service.extend_vote_session(session.id, additional_hours=24)
        assert session.extended_count == 1
        assert session.closes_at == original_closes + timedelta(hours=24)

        # Extend again
        session = await self.service.extend_vote_session(session.id, additional_hours=48)
        assert session.extended_count == 2
        assert session.closes_at == original_closes + timedelta(hours=72)

    @pytest.mark.asyncio
    async def test_cannot_vote_after_close(self):
        """Voting after deadline is rejected"""

        session = await self.service.create_vote(
            proposal_id="prop-closed",
            cell_id="sunrise-collective",
            duration_hours=1  # 1 hour
        )

        # Vote before close
        await self.service.cast_vote(session.id, "alice", VoteChoice.YES)

        # Fast-forward past close
        with freeze_time(session.closes_at + timedelta(minutes=1)):
            # Try to vote after close
            with pytest.raises(ValueError, match="Voting period has closed"):
                await self.service.cast_vote(session.id, "bob", VoteChoice.YES)

    @pytest.mark.asyncio
    async def test_cannot_vote_if_not_eligible(self):
        """Only eligible voters can vote"""

        session = await self.service.create_vote(
            proposal_id="prop-restricted",
            cell_id="sunrise-collective",
            duration_hours=24
        )

        # Try to vote as someone not in the cell
        with pytest.raises(ValueError, match="not eligible"):
            await self.service.cast_vote(session.id, "outsider", VoteChoice.YES)

    @pytest.mark.asyncio
    async def test_change_vote(self):
        """Users can change their vote before close"""

        session = await self.service.create_vote(
            proposal_id="prop-changeable",
            cell_id="sunrise-collective",
            duration_hours=24
        )

        # Vote yes
        await self.service.cast_vote(session.id, "alice", VoteChoice.YES)
        session = await self.service.get_session(session.id)
        assert session.votes["alice"] == VoteChoice.YES

        # Change to no
        await self.service.cast_vote(session.id, "alice", VoteChoice.NO)
        session = await self.service.get_session(session.id)
        assert session.votes["alice"] == VoteChoice.NO

    @pytest.mark.asyncio
    async def test_vote_result_tie(self):
        """Equal yes/no votes results in tie"""

        session = await self.service.create_vote(
            proposal_id="prop-tie",
            cell_id="sunrise-collective",
            duration_hours=1
        )

        # 2 yes, 2 no
        await self.service.cast_vote(session.id, "alice", VoteChoice.YES)
        await self.service.cast_vote(session.id, "bob", VoteChoice.YES)
        await self.service.cast_vote(session.id, "carol", VoteChoice.NO)
        await self.service.cast_vote(session.id, "dave", VoteChoice.NO)

        with freeze_time(session.closes_at + timedelta(hours=1)):
            final_session = await self.service.get_session(session.id)
            assert final_session.result == "tie"

    @pytest.mark.asyncio
    async def test_privacy_no_cross_session_tracking(self):
        """
        CRITICAL: Cannot track who is silent across multiple votes.

        bell hooks: Respecting silence IS respecting voice.
        """

        # Create two different votes
        session1 = await self.service.create_vote(
            proposal_id="prop-1",
            cell_id="sunrise-collective",
            duration_hours=24
        )

        session2 = await self.service.create_vote(
            proposal_id="prop-2",
            cell_id="sunrise-collective",
            duration_hours=24
        )

        # Alice votes in session1, not in session2
        await self.service.cast_vote(session1.id, "alice", VoteChoice.YES)

        # Bob doesn't vote in either
        # (Intentionally silent)

        # Verify: No way to query "Bob's silence pattern"
        # We can only see he's silent in THIS session, not across sessions

        metrics1 = await self.service.check_silence_weight(session1.id)
        metrics2 = await self.service.check_silence_weight(session2.id)

        # Session 1: Alice voted, Bob silent (among others)
        assert "bob" in await self._get_silent_voters(session1.id)

        # Session 2: Both silent
        assert "alice" in await self._get_silent_voters(session2.id)
        assert "bob" in await self._get_silent_voters(session2.id)

        # But: NO function to get "users who are always silent"
        assert not hasattr(self.service, "get_chronic_silent_voters")
        assert not hasattr(self.service, "get_user_silence_history")

    async def _get_silent_voters(self, session_id: str):
        """Helper to get silent voters for a session"""
        session = await self.service.get_session(session_id)
        return session.silent_voters


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
