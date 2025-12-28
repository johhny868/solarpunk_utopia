"""
Governance API - Endpoints for silence weight voting.

bell hooks: "The function of art is to do more than tell it like it is -
it's to imagine what is possible."
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from app.services.governance_service import GovernanceService, get_governance_service
from app.models.governance import (
    VoteSession,
    VoteChoice,
    CreateVoteRequest,
    CastVoteRequest,
    ExtendVoteRequest,
    SilenceMetrics
)


router = APIRouter(prefix="/api/governance", tags=["governance"])


# Dependency stubs - replace with actual auth
async def get_current_user() -> str:
    """Get current user ID (stub - replace with actual auth)"""
    return "current-user-id"


async def require_moderator() -> str:
    """Require moderator role (stub - replace with actual auth/RBAC)"""
    return "moderator-user-id"


@router.post("/votes/create", response_model=VoteSession)
async def create_vote_session(
    request: CreateVoteRequest,
    service: GovernanceService = Depends(get_governance_service)
):
    """
    Create a new vote session.

    For critical decisions, set quorum_required (e.g., 0.6 for 60% participation).
    """
    try:
        session = await service.create_vote(
            proposal_id=request.proposal_id,
            cell_id=request.cell_id,
            duration_hours=request.duration_hours,
            quorum_required=request.quorum_required
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/votes/{session_id}/cast", response_model=VoteSession)
async def cast_vote(
    session_id: str,
    request: CastVoteRequest,
    user_id: str = Depends(get_current_user),
    service: GovernanceService = Depends(get_governance_service)
):
    """
    Cast a vote (yes/no/abstain).

    Your voice matters, and so does your choice to abstain.
    """
    try:
        session = await service.cast_vote(
            session_id=session_id,
            user_id=user_id,
            choice=request.choice
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/votes/{session_id}/silence-metrics", response_model=SilenceMetrics)
async def get_silence_metrics(
    session_id: str,
    service: GovernanceService = Depends(get_governance_service)
):
    """
    Get silence weight and participation metrics.

    Surfaces how many people haven't voted yet, without shaming them.

    bell hooks: Don't assume silence = consent.
    """
    try:
        metrics = await service.check_silence_weight(session_id)
        return metrics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/votes/{session_id}/send-check-in")
async def send_check_in(
    session_id: str,
    moderator_id: str = Depends(require_moderator),
    service: GovernanceService = Depends(get_governance_service)
):
    """
    Send gentle check-in to silent voters.

    No pressure, no shaming. Just awareness.

    Privacy guarantee: Outreach record is ephemeral (auto-purged when vote closes).
    """
    try:
        outreach = await service.send_gentle_check_in(
            session_id=session_id,
            moderator_id=moderator_id
        )

        return {
            "success": True,
            "sent_to_count": len(outreach.sent_to),
            "message": "Gentle check-in sent to silent voters",
            "purge_at": outreach.purge_at
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/votes/{session_id}/extend", response_model=VoteSession)
async def extend_vote(
    session_id: str,
    request: ExtendVoteRequest,
    moderator_id: str = Depends(require_moderator),
    service: GovernanceService = Depends(get_governance_service)
):
    """
    Extend voting period (useful for low participation).

    When silence_weight is high, consider extending rather than deciding
    with minimal input.
    """
    try:
        session = await service.extend_vote_session(
            session_id=session_id,
            additional_hours=request.additional_hours
        )

        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/votes/active/{cell_id}", response_model=List[dict])
async def get_active_votes(
    cell_id: str,
    service: GovernanceService = Depends(get_governance_service)
):
    """
    Get active vote sessions for a cell, enriched with silence metrics.

    Shows which votes need attention (high silence_weight, no quorum, etc.)
    """
    sessions = await service.get_active_sessions(cell_id)

    # Enrich with silence metrics
    enriched = []
    for session in sessions:
        metrics = SilenceMetrics(
            silence_weight=session.silence_weight,
            participation_rate=session.participation_rate,
            should_pause=session.should_pause,
            has_quorum=session.has_quorum,
            silent_count=len(session.silent_voters),
            voted_count=len(session.votes),
            eligible_count=len(session.eligible_voters)
        )

        enriched.append({
            "session": session.dict(),
            "metrics": metrics.dict()
        })

    return enriched


@router.get("/votes/{session_id}", response_model=VoteSession)
async def get_vote_session(
    session_id: str,
    service: GovernanceService = Depends(get_governance_service)
):
    """Get a specific vote session"""
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Vote session not found")
    return session


@router.post("/votes/purge-outreach")
async def purge_outreach(
    moderator_id: str = Depends(require_moderator),
    service: GovernanceService = Depends(get_governance_service)
):
    """
    Manually trigger outreach purge (privacy protection).

    Normally runs automatically via background job.
    """
    deleted = await service.purge_expired_outreach()
    return {
        "success": True,
        "deleted_count": deleted,
        "message": f"Purged {deleted} expired outreach records"
    }
