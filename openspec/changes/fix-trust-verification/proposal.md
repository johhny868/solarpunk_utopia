# Proposal: Fix Trust Verification - Replace Hardcoded Values

**Submitted By:** Gap Analysis Agent
**Date:** 2025-12-19
**Status:** HIGH - WORKSHOP BLOCKER
**Gaps Addressed:** GAP-106, GAP-118, GAP-120
**Priority:** P0 - Before Workshop

## Problem Statement

Trust and authentication checks use hardcoded values instead of actual verification:

1. **GAP-118**: Sanctuary API always returns trust score 0.9
2. **GAP-120**: Economic withdrawal steward verification is TODO
3. **GAP-106**: Genesis node addition requires only single existing genesis (no multi-sig)

This means anyone can access high-trust features and a compromised genesis can add malicious accounts.

## Current State (Broken)

### Sanctuary API (`app/api/sanctuary.py:103-104`)
```python
# TODO: Get user's actual trust score from trust service
user_trust = 0.9  # Placeholder - always 0.9!
```
**Risk:** Anyone can access sanctuary locations regardless of trust.

### Economic Withdrawal (`app/api/economic_withdrawal.py:116`)
```python
# TODO: Verify user is steward
```
**Risk:** Anyone can create/modify boycott campaigns.

### Genesis Addition (`app/api/vouch.py:225-231`)
```python
if genesis_nodes:
    if not repo.is_genesis_node(current_user.id):
        raise HTTPException(...)
# Single genesis can add new genesis nodes!
```
**Risk:** Compromised genesis node can add trojan horse accounts.

## Proposed Solution

### 1. Integrate Real Trust Service

```python
# app/api/sanctuary.py

from app.services.web_of_trust_service import WebOfTrustService

@router.post("/spaces")
async def create_sanctuary_space(
    request: CreateSpaceRequest,
    current_user=Depends(get_current_user),
    trust_service: WebOfTrustService = Depends(get_trust_service),
):
    # Get ACTUAL trust score
    trust_score = trust_service.compute_trust_score(current_user.id)
    user_trust = trust_score.computed_trust

    if user_trust < TRUST_THRESHOLDS["steward_actions"]:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient trust for sanctuary operations. Need {TRUST_THRESHOLDS['steward_actions']}, have {user_trust:.2f}"
        )

    # Proceed with actual trust level
    ...
```

### 2. Steward Verification Decorator

```python
# app/auth/steward_auth.py

async def verify_steward(user_id: str, cell_id: str) -> bool:
    """Verify user is a steward of the specified cell"""
    cell = await cell_repo.get(cell_id)
    if not cell:
        return False
    return user_id in cell.steward_ids

def require_steward(cell_id_param: str = "cell_id"):
    """Decorator to require steward role for endpoint"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = get_request_from_args(args, kwargs)
            cell_id = kwargs.get(cell_id_param) or request.path_params.get(cell_id_param)

            if not await verify_steward(request.state.user.id, cell_id):
                raise HTTPException(
                    status_code=403,
                    detail="Steward role required for this action"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. Genesis Node Multi-Sig

```python
# app/api/vouch.py

GENESIS_THRESHOLD = 3  # 3 of 7 required

@router.post("/genesis/propose/{user_id}")
async def propose_genesis_node(
    user_id: str,
    current_user=Depends(get_current_user),
    repo: VouchRepository = Depends(get_vouch_repo),
):
    """Propose a new genesis node - requires 3 existing genesis signatures"""
    genesis_nodes = repo.get_genesis_nodes()

    if not repo.is_genesis_node(current_user.id):
        raise HTTPException(status_code=403, detail="Only genesis nodes can propose new genesis")

    # Create or update proposal
    proposal = repo.get_or_create_genesis_proposal(user_id)
    proposal.add_signature(current_user.id)

    if len(proposal.signatures) >= GENESIS_THRESHOLD:
        # Threshold met - add new genesis
        repo.add_genesis_node(user_id, added_by=proposal.signatures)
        repo.delete_genesis_proposal(user_id)
        return {"status": "approved", "user_id": user_id}

    remaining = GENESIS_THRESHOLD - len(proposal.signatures)
    return {
        "status": "pending",
        "user_id": user_id,
        "signatures": len(proposal.signatures),
        "remaining": remaining,
    }
```

### 4. Apply Steward Verification to Economic Withdrawal

```python
# app/api/economic_withdrawal.py

@router.post("/campaigns")
@require_steward("cell_id")
async def create_campaign(
    request: CreateCampaignRequest,
    current_user=Depends(get_current_user),
):
    """Create boycott campaign - steward only"""
    ...

@router.patch("/campaigns/{campaign_id}/approve")
@require_steward("cell_id")
async def approve_campaign(
    campaign_id: str,
    current_user=Depends(get_current_user),
):
    """Approve campaign - steward only"""
    ...
```

## Requirements

### SHALL Requirements
- SHALL use actual trust scores from WebOfTrustService
- SHALL verify steward role for all steward-only endpoints
- SHALL require 3-of-7 genesis signatures for new genesis nodes
- SHALL NOT use hardcoded trust values
- SHALL NOT allow single-actor admin operations

### MUST Requirements
- MUST deny access when trust is insufficient
- MUST log all trust-gated access attempts

## Testing

```python
def test_sanctuary_uses_real_trust():
    """Verify sanctuary checks actual trust score"""
    # User with low trust
    low_trust_user = create_user_with_trust(0.3)
    response = client.post("/sanctuary/spaces", user=low_trust_user)
    assert response.status_code == 403

    # User with high trust
    high_trust_user = create_user_with_trust(0.95)
    response = client.post("/sanctuary/spaces", user=high_trust_user)
    assert response.status_code == 200

def test_genesis_requires_multisig():
    """Verify genesis addition requires 3 signatures"""
    genesis_1 = create_genesis_node()

    # Single signature - should be pending
    response = client.post(f"/vouch/genesis/propose/{new_user}", user=genesis_1)
    assert response.json()["status"] == "pending"
    assert response.json()["remaining"] == 2

    # Add more signatures
    genesis_2 = create_genesis_node()
    genesis_3 = create_genesis_node()

    client.post(f"/vouch/genesis/propose/{new_user}", user=genesis_2)
    response = client.post(f"/vouch/genesis/propose/{new_user}", user=genesis_3)

    assert response.json()["status"] == "approved"
```

## Files to Modify

1. `app/api/sanctuary.py:103-104, 136, 141`
2. `app/api/economic_withdrawal.py:116, 238, 385, 471`
3. `app/api/vouch.py:206-251`
4. New: `app/auth/steward_auth.py`

## Effort Estimate

- 3 hours implementation
- 1 hour testing
- 30 min documentation

## Success Criteria

- [ ] All trust checks use actual WebOfTrustService
- [ ] All steward endpoints verify steward role
- [ ] Genesis addition requires 3-of-7 signatures
- [ ] No hardcoded trust values in codebase
- [ ] All TODO comments in affected files resolved
