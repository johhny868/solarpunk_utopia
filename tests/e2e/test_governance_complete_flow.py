"""
Complete end-to-end governance flow test (GAP-60).

bell hooks: "The function of art is to do more than tell it like it is -
it's to imagine what is possible."

This test validates the complete silence weight governance flow from creation to completion.
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from freezegun import freeze_time

from app.models.governance import VoteChoice
from app.database.governance_repository import GovernanceRepository
from app.services.governance_service import GovernanceService


@pytest.mark.asyncio
async def test_complete_governance_flow():
    """
    Complete E2E flow: create vote → cast votes → check silence → extend → close

    Validates:
    - Vote creation with quorum requirements
    - Silence weight calculation (70% -> 50% -> 40%)
    - Gentle check-in to silent voters (ephemeral)
    - Vote extension for low participation
    - Quorum enforcement
    - Vote result determination
    - Privacy guarantees (outreach purge)
    """

    # Setup: Create temp database
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    try:
        # Run migration
        import aiosqlite
        async with aiosqlite.connect(db_path) as db:
            with open("app/database/migrations/004_governance_silence_weight.sql") as f:
                migration_sql = f.read()
            await db.executescript(migration_sql)
            await db.commit()

        # Create service
        repo = GovernanceRepository(db_path)
        service = GovernanceService(repo)

        # Mock cell members
        async def mock_get_cell_members(cell_id: str):
            return ["alice", "bob", "carol", "dave", "eve",
                    "frank", "grace", "hank", "iris", "jack"]

        service._get_cell_members = mock_get_cell_members

        # Step 1: Create vote session (quorum = 50%)
        session = await service.create_vote(
            proposal_id="prop-mutual-aid",
            cell_id="sunrise-collective",
            duration_hours=24,
            quorum_required=0.5
        )

        assert session.id is not None
        assert len(session.eligible_voters) == 10
        assert session.silence_weight == 1.0  # 100% silent initially

        # Step 2: Three people vote (30% participation, 70% silent)
        await service.cast_vote(session.id, "alice", VoteChoice.YES)
        await service.cast_vote(session.id, "bob", VoteChoice.YES)
        await service.cast_vote(session.id, "carol", VoteChoice.NO)

        metrics = await service.check_silence_weight(session.id)
        assert metrics.silence_weight == 0.7
        assert metrics.should_pause == True  # bell hooks: More silent than voted
        assert metrics.has_quorum == False  # Below 50%
        assert "7 people" in metrics.prompt  # Gentle reminder

        # Step 3: Send gentle check-in (no shaming!)
        outreach = await service.send_gentle_check_in(
            session_id=session.id,
            moderator_id="facilitator"
        )

        assert len(outreach.sent_to) == 7  # 7 silent voters
        assert "No pressure" in outreach.message  # Respectful tone
        assert outreach.purge_at == session.closes_at  # Will be purged

        # Step 4: Extend vote for low participation
        extended_session = await service.extend_vote_session(
            session_id=session.id,
            additional_hours=48
        )

        assert extended_session.extended_count == 1

        # Step 5: Two more people vote (50% participation = quorum met!)
        await service.cast_vote(session.id, "dave", VoteChoice.YES)
        await service.cast_vote(session.id, "eve", VoteChoice.ABSTAIN)

        metrics = await service.check_silence_weight(session.id)
        assert metrics.participation_rate == 0.5  # Exactly 50%
        assert metrics.has_quorum == True  # Met quorum!

        # Step 6: One more vote for good measure (60% participation)
        await service.cast_vote(session.id, "frank", VoteChoice.YES)

        metrics = await service.check_silence_weight(session.id)
        assert metrics.silence_weight == 0.4  # 4 silent out of 10
        assert metrics.should_pause == False  # More voted than silent

        # Step 7: Fast-forward to vote close
        with freeze_time(extended_session.closes_at + timedelta(hours=1)):
            final_session = await service.get_session(session.id)

            assert final_session.is_closed == True
            assert final_session.result == "passed"  # 4 yes, 1 no, 1 abstain
            assert final_session.has_quorum == True

            # Step 8: Privacy guarantee - outreach record purged
            purged = await service.purge_expired_outreach()
            assert purged >= 1

            retrieved_outreach = await repo.get_outreach(outreach.id)
            assert retrieved_outreach is None  # Ephemeral! No tracking!

        print("\n✅ Complete E2E governance flow validated!")
        print(f"   - Silence weight tracked (100% → 70% → 50% → 40%)")
        print(f"   - Quorum enforced (50% required)")
        print(f"   - Gentle check-in sent (no shaming)")
        print(f"   - Vote extended for participation")
        print(f"   - Privacy protected (outreach purged)")
        print(f"   - bell hooks would approve! 🌟")

    finally:
        # Cleanup
        os.close(db_fd)
        os.unlink(db_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
