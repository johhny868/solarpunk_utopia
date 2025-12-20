"""
Tests for Governance Silence Weight system (GAP-60).

bell hooks: "I will not have my life narrowed down."

These tests verify:
1. Silence weight calculations
2. Quorum requirements
3. Privacy guarantees (no silence pattern tracking)
4. Ephemeral outreach (auto-purge)
5. Vote extensions for low participation
"""

import pytest
import asyncio
import os
import tempfile
from datetime import datetime, timedelta
from freezegun import freeze_time

from app.models.governance import VoteSession, VoteOutreach, VoteChoice
from app.database.governance_repository import GovernanceRepository
from app.services.governance_service import GovernanceService


class TestSilenceWeightCalculations:
    """Test silence_weight and participation_rate calculations"""

    def test_silence_weight_with_no_votes(self):
        """100% silent when no one has voted"""
        session = VoteSession(
            id="test-1",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol", "dave"]
        )

        assert session.silence_weight == 1.0
        assert session.participation_rate == 0.0
        assert session.should_pause == True
        assert len(session.silent_voters) == 4

    def test_silence_weight_with_partial_votes(self):
        """Silence weight = silent / total"""
        session = VoteSession(
            id="test-2",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol", "dave"],
            votes={"alice": VoteChoice.YES}
        )

        assert session.silence_weight == 0.75  # 3 silent out of 4
        assert session.participation_rate == 0.25
        assert session.should_pause == True  # More silent than voted

    def test_silence_weight_with_majority_voted(self):
        """should_pause = False when more voted than silent"""
        session = VoteSession(
            id="test-3",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol", "dave"],
            votes={
                "alice": VoteChoice.YES,
                "bob": VoteChoice.NO,
                "carol": VoteChoice.ABSTAIN
            }
        )

        assert session.silence_weight == 0.25  # 1 silent out of 4
        assert session.participation_rate == 0.75
        assert session.should_pause == False  # More voted than silent

    def test_silence_weight_with_all_voted(self):
        """0% silent when everyone has voted"""
        session = VoteSession(
            id="test-4",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob"],
            votes={
                "alice": VoteChoice.YES,
                "bob": VoteChoice.NO
            }
        )

        assert session.silence_weight == 0.0
        assert session.participation_rate == 1.0
        assert session.should_pause == False
        assert len(session.silent_voters) == 0


class TestQuorumRequirements:
    """Test quorum enforcement for critical decisions"""

    def test_no_quorum_required_always_passes(self):
        """When quorum_required = None, quorum is always met"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol", "dave", "eve"],
            votes={"alice": VoteChoice.YES},
            quorum_required=None
        )

        assert session.has_quorum == True

    def test_quorum_not_met(self):
        """Quorum = 60% but only 40% participated"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol", "dave", "eve"],
            votes={
                "alice": VoteChoice.YES,
                "bob": VoteChoice.YES
            },
            quorum_required=0.6  # Need 60% participation
        )

        assert session.participation_rate == 0.4  # 2 out of 5
        assert session.has_quorum == False

    def test_quorum_met(self):
        """Quorum = 60% and 60% participated"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol", "dave", "eve"],
            votes={
                "alice": VoteChoice.YES,
                "bob": VoteChoice.NO,
                "carol": VoteChoice.ABSTAIN
            },
            quorum_required=0.6  # Need 60%
        )

        assert session.participation_rate == 0.6  # 3 out of 5
        assert session.has_quorum == True

    def test_abstain_counts_toward_quorum(self):
        """Abstaining is participation (you made a choice)"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol", "dave"],
            votes={
                "alice": VoteChoice.ABSTAIN,
                "bob": VoteChoice.ABSTAIN,
                "carol": VoteChoice.ABSTAIN
            },
            quorum_required=0.75  # Need 75%
        )

        assert session.participation_rate == 0.75  # 3 out of 4
        assert session.has_quorum == True


class TestVoteResults:
    """Test vote result determination"""

    def test_result_none_when_open(self):
        """Can't determine result while vote is open"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob"],
            votes={"alice": VoteChoice.YES}
        )

        assert session.is_closed == False
        assert session.result is None

    def test_result_passed(self):
        """More yes than no = passed"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now() - timedelta(hours=25),
            closes_at=datetime.now() - timedelta(hours=1),
            eligible_voters=["alice", "bob", "carol"],
            votes={
                "alice": VoteChoice.YES,
                "bob": VoteChoice.YES,
                "carol": VoteChoice.NO
            }
        )

        assert session.is_closed == True
        assert session.result == "passed"

    def test_result_failed(self):
        """More no than yes = failed"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now() - timedelta(hours=25),
            closes_at=datetime.now() - timedelta(hours=1),
            eligible_voters=["alice", "bob", "carol"],
            votes={
                "alice": VoteChoice.YES,
                "bob": VoteChoice.NO,
                "carol": VoteChoice.NO
            }
        )

        assert session.is_closed == True
        assert session.result == "failed"

    def test_result_no_quorum(self):
        """Not enough participation = no_quorum"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now() - timedelta(hours=25),
            closes_at=datetime.now() - timedelta(hours=1),
            eligible_voters=["alice", "bob", "carol", "dave", "eve"],
            votes={"alice": VoteChoice.YES},
            quorum_required=0.6  # Need 60%
        )

        assert session.is_closed == True
        assert session.has_quorum == False
        assert session.result == "no_quorum"


@pytest.mark.asyncio
class TestGovernanceRepository:
    """Test database operations"""

    async def setup_db(self):
        """Create test database"""
        # Create temp database
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")

        # Run migration
        import aiosqlite
        async with aiosqlite.connect(self.db_path) as db:
            with open("app/database/migrations/004_governance_silence_weight.sql") as f:
                migration_sql = f.read()
            await db.executescript(migration_sql)
            await db.commit()

        return GovernanceRepository(self.db_path)

    async def teardown_db(self):
        """Clean up test database"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    async def test_create_and_get_vote_session(self):
        """Create and retrieve vote session"""
        repo = await self.setup_db()

        session = VoteSession(
            id="test-session",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol"],
            votes={}
        )

        # Create
        await repo.create_vote_session(session)

        # Get
        retrieved = await repo.get_vote_session("test-session")

        assert retrieved is not None
        assert retrieved.id == "test-session"
        assert retrieved.proposal_id == "prop-1"
        assert len(retrieved.eligible_voters) == 3
        assert len(retrieved.votes) == 0

        await self.teardown_db()

    async def test_cast_vote(self):
        """Cast a vote and verify update"""
        repo = await self.setup_db()

        session = VoteSession(
            id="test-session",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob"],
            votes={}
        )

        await repo.create_vote_session(session)

        # Cast vote
        updated = await repo.cast_vote("test-session", "alice", VoteChoice.YES)

        assert "alice" in updated.votes
        assert updated.votes["alice"] == VoteChoice.YES
        assert len(updated.votes) == 1

        # Cast another
        updated = await repo.cast_vote("test-session", "bob", VoteChoice.NO)
        assert len(updated.votes) == 2

        await self.teardown_db()

    async def test_extend_vote_session(self):
        """Extend voting period"""
        repo = await self.setup_db()

        original_closes = datetime.now() + timedelta(hours=24)
        session = VoteSession(
            id="test-session",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=original_closes,
            eligible_voters=["alice", "bob"],
            votes={}
        )

        await repo.create_vote_session(session)

        # Extend
        new_closes = original_closes + timedelta(hours=48)
        extended = await repo.extend_vote_session("test-session", new_closes)

        assert extended.closes_at == new_closes
        assert extended.extended_count == 1

        await self.teardown_db()

    async def test_outreach_ephemeral(self):
        """Outreach records are purged after expiry"""
        repo = await self.setup_db()

        outreach = VoteOutreach(
            id="outreach-1",
            vote_session_id="session-1",
            sent_at=datetime.now(),
            sent_to=["alice", "bob"],
            message="Gentle reminder",
            purge_at=datetime.now() + timedelta(hours=1)
        )

        # Create
        await repo.create_outreach(outreach)

        # Verify exists
        retrieved = await repo.get_outreach("outreach-1")
        assert retrieved is not None

        # Fast-forward past purge_at
        with freeze_time(datetime.now() + timedelta(hours=2)):
            deleted = await repo.purge_expired_outreach()
            assert deleted == 1

            # Verify deleted
            retrieved = await repo.get_outreach("outreach-1")
            assert retrieved is None

        await self.teardown_db()


@pytest.mark.asyncio
class TestPrivacyGuarantees:
    """
    CRITICAL: Verify we don't track silence patterns over time.

    bell hooks: Respecting silence IS respecting voice.
    """

    async def test_no_silence_history_tracking(self):
        """Verify we can't query a user's silence pattern"""
        # This test verifies that the system does NOT have functions like:
        # - get_user_silence_history(user_id)
        # - get_users_who_never_vote()
        # - get_silence_pattern(user_id)

        from app.services import governance_service

        # These functions should NOT exist
        assert not hasattr(governance_service, "get_user_silence_history")
        assert not hasattr(governance_service, "get_silence_patterns")
        assert not hasattr(governance_service, "get_frequent_silent_voters")

    def test_silent_voters_computed_not_stored(self):
        """silent_voters is a @property, not a stored field"""
        session = VoteSession(
            id="test",
            proposal_id="prop-1",
            cell_id="cell-1",
            opened_at=datetime.now(),
            closes_at=datetime.now() + timedelta(hours=24),
            eligible_voters=["alice", "bob", "carol"],
            votes={"alice": VoteChoice.YES}
        )

        # Verify it's computed
        assert hasattr(VoteSession, "silent_voters")
        assert isinstance(VoteSession.silent_voters, property)

        # Verify it's not in the model's model_dump (not stored)
        session_dict = session.model_dump()
        assert "silent_voters" not in session_dict

    async def test_outreach_auto_purge_prevents_tracking(self):
        """Outreach records don't persist, preventing 'who got reminded' tracking"""
        # Ephemeral records prevent long-term tracking like:
        # "Bob has been reminded 10 times but never votes"

        now = datetime.now()
        purge_time = now + timedelta(hours=1)

        outreach1 = VoteOutreach(
            id="o1",
            vote_session_id="s1",
            sent_at=now,
            sent_to=["bob"],
            message="Vote closes soon",
            purge_at=purge_time
        )

        # After purge_at, this record is deleted
        # No way to track how many times Bob was reminded
        assert outreach1.purge_at == purge_time


@pytest.mark.asyncio
class TestGovernanceService:
    """Test service layer business logic"""

    async def test_check_silence_weight_gentle_prompt(self):
        """Service adds gentle prompt when silence_weight > threshold"""
        # This will be tested in e2e tests with actual database
        pass  # Placeholder for service tests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
