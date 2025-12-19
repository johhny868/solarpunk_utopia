# Proposal: Fix Frontend/Backend API Mismatches

**Submitted By:** Gap Analysis Agent
**Date:** 2025-12-19
**Status:** CRITICAL - WORKSHOP BLOCKER
**Gaps Addressed:** GAP-65, GAP-69, GAP-71, GAP-72
**Priority:** P0 - Before Workshop

## Problem Statement

Frontend calls endpoints that don't exist or have different signatures:

1. **GAP-65**: Frontend calls `/matches/{id}/accept` and `/matches/{id}/reject` but backend has `/matches/{id}/approve`
2. **GAP-69**: Frontend calls `/vf/commitments` but endpoint doesn't exist
3. **GAP-71**: DELETE listings has no ownership verification
4. **GAP-72**: Reject endpoint uses `request.user_id` which doesn't exist

## Current State (Broken)

### Match Accept/Reject (`frontend/src/api/valueflows.ts:137-145`)
```typescript
// Frontend calls:
acceptMatch: async (id: string): Promise<Match> => {
  const response = await api.post<Match>(`/matches/${id}/accept`);
  ...
}
```

```python
# Backend has:
@router.patch("/{match_id}/approve", response_model=dict)
async def approve_match(match_id: str, agent_id: str):  # Different endpoint!
```

### Commitments Endpoint
```typescript
// Frontend expects:
getCommitments: async (): Promise<Commitment[]> => {
  const response = await api.get<Commitment[]>('/commitments');
```
No backend endpoint exists.

### Delete Listing (`valueflows_node/app/api/vf/listings.py:231-233`)
```python
# TODO (GAP-02): Add ownership verification when auth is implemented
# if listing.agent_id != request.state.user.id:
#     raise HTTPException(status_code=403, detail="Not authorized")
```

### Reject Endpoint (`app/api/agents.py:205`)
```python
proposal = await approval_tracker.approve_proposal(
    proposal_id=proposal_id,
    user_id=request.user_id,  # ApprovalRequest has no user_id field!
```

## Proposed Solution

### 1. Add Accept/Reject Match Endpoints

```python
# valueflows_node/app/api/vf/matches.py

@router.post("/{match_id}/accept", response_model=dict)
async def accept_match(
    match_id: str,
    current_user=Depends(get_current_user),
    repo: MatchRepository = Depends(get_match_repo),
):
    """Accept a match - called by the person who posted the need"""
    match = await repo.get(match_id)
    if not match:
        raise HTTPException(404, "Match not found")

    # Verify caller is the need owner
    if match.need_agent_id != current_user.id:
        raise HTTPException(403, "Only the need owner can accept matches")

    match.status = "accepted"
    match.accepted_at = datetime.utcnow()
    await repo.update(match)

    return {"status": "accepted", "match_id": match_id}


@router.post("/{match_id}/reject", response_model=dict)
async def reject_match(
    match_id: str,
    reason: str = None,
    current_user=Depends(get_current_user),
    repo: MatchRepository = Depends(get_match_repo),
):
    """Reject a match"""
    match = await repo.get(match_id)
    if not match:
        raise HTTPException(404, "Match not found")

    # Either party can reject
    if current_user.id not in [match.need_agent_id, match.offer_agent_id]:
        raise HTTPException(403, "Only match participants can reject")

    match.status = "rejected"
    match.rejected_at = datetime.utcnow()
    match.rejection_reason = reason
    await repo.update(match)

    return {"status": "rejected", "match_id": match_id}
```

### 2. Add Commitments Endpoint

```python
# valueflows_node/app/api/vf/commitments.py

from fastapi import APIRouter, Depends
from typing import List
from app.models.commitment import Commitment
from app.database.commitment_repository import CommitmentRepository

router = APIRouter(prefix="/commitments", tags=["commitments"])


@router.get("/", response_model=List[Commitment])
async def get_commitments(
    current_user=Depends(get_current_user),
    repo: CommitmentRepository = Depends(get_commitment_repo),
    status: str = None,
):
    """Get all commitments for current user"""
    return await repo.get_by_agent(current_user.id, status=status)


@router.get("/{commitment_id}", response_model=Commitment)
async def get_commitment(
    commitment_id: str,
    repo: CommitmentRepository = Depends(get_commitment_repo),
):
    """Get a specific commitment"""
    commitment = await repo.get(commitment_id)
    if not commitment:
        raise HTTPException(404, "Commitment not found")
    return commitment


@router.post("/", response_model=Commitment)
async def create_commitment(
    request: CreateCommitmentRequest,
    current_user=Depends(get_current_user),
    repo: CommitmentRepository = Depends(get_commitment_repo),
):
    """Create a new commitment"""
    commitment = Commitment(
        id=str(uuid4()),
        provider_id=current_user.id,
        receiver_id=request.receiver_id,
        resource_specification_id=request.resource_specification_id,
        quantity=request.quantity,
        due_date=request.due_date,
        status="pending",
    )
    await repo.create(commitment)
    return commitment
```

### 3. Fix Listing Deletion with Ownership Check

```python
# valueflows_node/app/api/vf/listings.py

@router.delete("/{listing_id}")
async def delete_listing(
    listing_id: str,
    current_user=Depends(get_current_user),
    repo: ListingRepository = Depends(get_listing_repo),
):
    """Delete a listing - only owner can delete"""
    listing = await repo.get(listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")

    # Ownership check
    if listing.agent_id != current_user.id:
        raise HTTPException(403, "Not authorized to delete this listing")

    await repo.delete(listing_id)
    return {"status": "deleted", "listing_id": listing_id}
```

### 4. Fix Reject Endpoint User ID

```python
# app/api/agents.py

class ApprovalRequest(BaseModel):
    approved: bool
    notes: str = None
    # user_id comes from auth, not request body


@router.post("/proposals/{proposal_id}/review")
async def review_proposal(
    proposal_id: str,
    request: ApprovalRequest,
    current_user=Depends(get_current_user),  # Get user from auth
):
    if request.approved:
        proposal = await approval_tracker.approve_proposal(
            proposal_id=proposal_id,
            user_id=current_user.id,  # From auth middleware
            notes=request.notes,
        )
    else:
        proposal = await approval_tracker.reject_proposal(
            proposal_id=proposal_id,
            user_id=current_user.id,  # From auth middleware
            notes=request.notes,
        )

    return proposal
```

## Requirements

### SHALL Requirements
- SHALL provide `/matches/{id}/accept` endpoint
- SHALL provide `/matches/{id}/reject` endpoint
- SHALL provide `/vf/commitments` CRUD endpoints
- SHALL verify ownership before listing deletion
- SHALL use authenticated user ID for all user-specific operations

### MUST Requirements
- MUST maintain API compatibility with frontend
- MUST return appropriate error codes (401, 403, 404)

## Testing

```python
def test_match_accept():
    match = create_test_match()
    need_owner = match.need_agent_id

    response = client.post(f"/matches/{match.id}/accept", user=need_owner)
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"

def test_match_accept_unauthorized():
    match = create_test_match()
    other_user = create_user()

    response = client.post(f"/matches/{match.id}/accept", user=other_user)
    assert response.status_code == 403

def test_commitments_endpoint_exists():
    response = client.get("/vf/commitments", user=test_user)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_listing_requires_ownership():
    listing = create_listing(owner=user_a)

    # Other user cannot delete
    response = client.delete(f"/listings/{listing.id}", user=user_b)
    assert response.status_code == 403

    # Owner can delete
    response = client.delete(f"/listings/{listing.id}", user=user_a)
    assert response.status_code == 200
```

## Files to Modify/Create

1. `valueflows_node/app/api/vf/matches.py` - Add accept/reject
2. New: `valueflows_node/app/api/vf/commitments.py`
3. `valueflows_node/app/api/vf/listings.py` - Add ownership check
4. `app/api/agents.py` - Fix user_id access
5. `valueflows_node/app/main.py` - Register commitments router

## Effort Estimate

- Accept/Reject endpoints: 1 hour
- Commitments CRUD: 2 hours
- Ownership verification: 30 min
- Reject endpoint fix: 15 min
- Testing: 1 hour
- Total: ~5 hours

## Success Criteria

- [ ] Frontend can accept matches
- [ ] Frontend can reject matches
- [ ] Frontend can fetch commitments
- [ ] Listing deletion requires ownership
- [ ] Proposal rejection uses auth user
- [ ] All frontend/backend contracts aligned
