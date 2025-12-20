# Proposal: Multi-Steward Sanctuary Verification (GAP-109)

**Submitted By:** Autonomous Development Agent
**Date:** 2025-12-19
**Status:** Draft
**Complexity:** Database migration + verification logic
**Timeline:** URGENT - Pre-Workshop
**Related:** GAP-109 (CRITICAL), SAFETY-01 from FRAUD_ABUSE_SAFETY.md

## Problem Statement

Current sanctuary verification allows a SINGLE steward to approve high-risk safe spaces. This creates a massive vulnerability:

- **Infiltrator steward** approves fake safe house → people walk into a trap
- **Compromised steward** under duress approves hostile location
- **Corrupted steward** sells sanctuary locations to adversaries
- **No accountability** - one person can endanger entire network

Sanctuary is the HIGHEST RISK operation. A compromised sanctuary can lead to:
- Arrests and deportations
- Violence against vulnerable people
- Exposure of the entire sanctuary network
- Loss of trust that destroys the community

**We cannot trust a single person with this responsibility.**

## Proposed Solution

Require **at least 2 independent steward verifications** before a sanctuary resource becomes available for matching.

### Verification Requirements

```python
class SanctuaryVerification:
    resource_id: str
    verified_by: List[str]  # At least 2 steward IDs
    verifications: List[VerificationRecord]
    first_verified_at: datetime
    last_check: datetime
    expires_at: datetime  # 90 days from last check

    @property
    def is_valid(self) -> bool:
        # Require at least 2 stewards
        if len(self.verified_by) < 2:
            return False

        # Require re-verification every 90 days
        if (now() - self.last_check).days > 90:
            return False

        return True

class VerificationRecord:
    steward_id: str
    verified_at: datetime
    verification_method: str  # "in_person", "video_call", "trusted_referral"
    notes: str  # Encrypted, steward-only
    escape_routes_verified: bool
    capacity_verified: bool
    buddy_protocol_available: bool
```

### Verification Process

1. **First Steward Verifies**
   - Visits location OR video call with owner
   - Checks escape routes, capacity, safety
   - Resource status: `PENDING` (not yet available for matching)
   - Other stewards notified: "Sanctuary X needs 2nd verification"

2. **Second Steward Verifies** (must be different person)
   - Independent verification (not told results of first)
   - Different day/time than first verification
   - Checks same safety criteria
   - Resource status: `VERIFIED` → available for matching

3. **Re-Verification Every 90 Days**
   - 2 weeks before expiry, stewards notified
   - At least 1 steward must re-verify
   - If no re-verification, status → `EXPIRED`
   - Expired sanctuaries not available for matching

### For Critical Needs

When assigning sanctuary for CRITICAL severity needs:
- Require sanctuary with **3+ successful prior uses**
- Prefer sanctuaries verified by 3+ stewards
- Buddy system mandatory (check-in every 4 hours)
- Escape plan required

## Requirements

### Requirement: Multi-Steward Verification

The system SHALL require multiple steward approvals for sanctuary resources.

#### Scenario: First Steward Verifies
- GIVEN Maria offers a safe space for emergency housing
- WHEN Steward Alice visits and approves the space
- THEN the resource is marked `PENDING` (not `VERIFIED`)
- AND Alice's verification is recorded with timestamp and notes
- AND other stewards in the cell are notified it needs 2nd verification
- AND the resource does NOT appear in matches yet

#### Scenario: Second Steward Completes Verification
- GIVEN Alice has already verified Maria's safe space
- WHEN Steward Bob independently verifies the space (different day)
- THEN the resource status changes to `VERIFIED`
- AND the resource becomes available for sanctuary matching
- AND both verifications are recorded

#### Scenario: Single Steward Verification Blocked
- GIVEN Maria's safe space has only 1 steward verification (Alice)
- WHEN Alice tries to verify again
- THEN the system rejects it: "Different steward required"
- AND the resource remains `PENDING`

### Requirement: Verification Expiration

The system SHALL expire sanctuary verifications after 90 days.

#### Scenario: Verification Expires
- GIVEN a sanctuary was verified 91 days ago
- WHEN the system checks verification status
- THEN the sanctuary status changes to `EXPIRED`
- AND the sanctuary is removed from available matches
- AND the stewards are notified: "Sanctuary X needs re-verification"

#### Scenario: Re-Verification Before Expiry
- GIVEN a sanctuary verified 80 days ago (10 days until expiry)
- WHEN a steward re-verifies the sanctuary
- THEN the `last_check` timestamp updates to now
- AND `expires_at` extends to 90 days from now
- AND the sanctuary remains `VERIFIED`

### Requirement: Track Successful Uses

The system SHALL track successful sanctuary uses for quality filtering.

#### Scenario: Critical Need Matching
- GIVEN someone needs CRITICAL severity sanctuary (life in danger)
- WHEN the system searches for available sanctuaries
- THEN it filters to sanctuaries with 3+ successful prior uses
- AND prefers sanctuaries with more steward verifications
- AND excludes newly verified sanctuaries (less than 1 month old)

## Database Changes

### New Table: sanctuary_verifications

```sql
CREATE TABLE sanctuary_verifications (
    id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL,
    steward_id TEXT NOT NULL,
    verified_at TIMESTAMP NOT NULL,
    verification_method TEXT NOT NULL, -- in_person, video_call, trusted_referral
    notes TEXT,  -- Encrypted
    escape_routes_verified BOOLEAN DEFAULT FALSE,
    capacity_verified BOOLEAN DEFAULT FALSE,
    buddy_protocol_available BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resource_id) REFERENCES sanctuary_resources(id),
    UNIQUE(resource_id, steward_id)  -- One verification per steward per resource
);

CREATE INDEX idx_sanctuary_verifications_resource
    ON sanctuary_verifications(resource_id);
CREATE INDEX idx_sanctuary_verifications_steward
    ON sanctuary_verifications(steward_id);
```

### New Table: sanctuary_uses

```sql
CREATE TABLE sanctuary_uses (
    id TEXT PRIMARY KEY,
    resource_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    completed_at TIMESTAMP NOT NULL,
    outcome TEXT NOT NULL,  -- success, failed, compromised
    purge_at TIMESTAMP NOT NULL,  -- Auto-delete after 30 days
    FOREIGN KEY (resource_id) REFERENCES sanctuary_resources(id)
);

CREATE INDEX idx_sanctuary_uses_resource
    ON sanctuary_uses(resource_id);
```

### Update sanctuary_resources Table

```sql
ALTER TABLE sanctuary_resources
    ADD COLUMN first_verified_at TIMESTAMP;
ALTER TABLE sanctuary_resources
    ADD COLUMN last_check TIMESTAMP;
ALTER TABLE sanctuary_resources
    ADD COLUMN expires_at TIMESTAMP;
ALTER TABLE sanctuary_resources
    ADD COLUMN successful_uses INTEGER DEFAULT 0;
```

## API Changes

### New Endpoint: POST /sanctuary/resources/{id}/verify

```python
@router.post("/resources/{resource_id}/verify")
async def verify_sanctuary_resource(
    resource_id: str,
    request: VerifyResourceRequest,
    steward_id: str = Depends(require_steward),
    service: SanctuaryService = Depends(get_sanctuary_service)
):
    """Steward verifies a sanctuary resource.

    Requires 2 independent steward verifications before resource becomes available.
    """
    verification = await service.add_verification(
        resource_id=resource_id,
        steward_id=steward_id,
        verification_method=request.method,
        notes=request.notes,
        escape_routes_verified=request.escape_routes_verified,
        capacity_verified=request.capacity_verified,
        buddy_protocol_available=request.buddy_protocol_available
    )

    resource = await service.get_resource(resource_id)

    return {
        "success": True,
        "verification_count": len(resource.verifications),
        "status": resource.verification_status,
        "needs_second_verification": resource.verification_status == "PENDING",
        "message": "Verification added. Needs 2nd steward to approve." if resource.verification_status == "PENDING" else "Resource verified and available for matching."
    }
```

### New Endpoint: GET /sanctuary/resources/needs-verification

```python
@router.get("/resources/needs-verification")
async def get_resources_needing_verification(
    cell_id: str,
    steward_id: str = Depends(require_steward),
    service: SanctuaryService = Depends(get_sanctuary_service)
):
    """Get sanctuary resources that need verification or re-verification.

    Returns:
    - Resources with only 1 verification (needs 2nd steward)
    - Resources expiring in next 14 days (needs re-verification)
    """
    resources = await service.get_resources_needing_verification(
        cell_id=cell_id,
        steward_id=steward_id  # Exclude resources this steward already verified
    )

    return {
        "pending_verification": resources.pending,  # Need 2nd steward
        "expiring_soon": resources.expiring,  # Need re-verification
    }
```

## Implementation Tasks

1. [ ] Create database migration for new tables and columns
2. [ ] Update SanctuaryResource model with verification fields
3. [ ] Create VerificationRecord and SanctuaryVerification models
4. [ ] Implement add_verification() in SanctuaryService
5. [ ] Implement get_resources_needing_verification()
6. [ ] Update offer_resource() to set status=PENDING by default
7. [ ] Add verification count check before matching
8. [ ] Implement re-verification expiry checks (background job)
9. [ ] Update sanctuary dashboard to show verification status
10. [ ] Create steward notification for verification needs
11. [ ] Add successful_uses tracking on match completion
12. [ ] Implement critical need filtering (3+ uses, 3+ verifications)

## Testing

```python
def test_single_steward_verification_not_enough():
    """Resource needs 2 stewards to verify"""
    resource = offer_sanctuary("safe_space", user_id="maria")
    assert resource.status == "PENDING"

    add_verification(resource.id, steward_id="alice")
    resource = get_resource(resource.id)
    assert resource.status == "PENDING"  # Still pending!
    assert len(resource.verifications) == 1

    # Should not appear in matches yet
    matches = get_available_sanctuaries(cell_id)
    assert resource.id not in [m.id for m in matches]

def test_two_steward_verification_succeeds():
    """Resource verified after 2 stewards approve"""
    resource = offer_sanctuary("safe_space", user_id="maria")

    add_verification(resource.id, steward_id="alice")
    add_verification(resource.id, steward_id="bob")

    resource = get_resource(resource.id)
    assert resource.status == "VERIFIED"
    assert len(resource.verifications) == 2

    # Now appears in matches
    matches = get_available_sanctuaries(cell_id)
    assert resource.id in [m.id for m in matches]

def test_same_steward_cannot_verify_twice():
    """Prevent single steward from verifying alone"""
    resource = offer_sanctuary("safe_space", user_id="maria")

    add_verification(resource.id, steward_id="alice")

    with pytest.raises(ValueError, match="Different steward required"):
        add_verification(resource.id, steward_id="alice")

def test_verification_expires_after_90_days():
    """Sanctuaries need re-verification"""
    resource = offer_sanctuary("safe_space", user_id="maria")
    add_verification(resource.id, steward_id="alice")
    add_verification(resource.id, steward_id="bob")

    # Fast-forward 91 days
    with freeze_time(datetime.now() + timedelta(days=91)):
        check_verification_expiry()  # Background job

        resource = get_resource(resource.id)
        assert resource.status == "EXPIRED"

        # Should not appear in matches
        matches = get_available_sanctuaries(cell_id)
        assert resource.id not in [m.id for m in matches]

def test_critical_needs_require_proven_sanctuaries():
    """Life-or-death situations need battle-tested sanctuaries"""
    # New sanctuary (only 1 week old)
    new_resource = create_verified_sanctuary(age_days=7, successful_uses=1)

    # Proven sanctuary (3 months old, 5 successful uses)
    proven_resource = create_verified_sanctuary(age_days=90, successful_uses=5)

    matches = get_available_sanctuaries(
        cell_id,
        severity="CRITICAL"
    )

    # Only proven sanctuary appears
    assert proven_resource.id in [m.id for m in matches]
    assert new_resource.id not in [m.id for m in matches]
```

## Security Considerations

### Attack: Infiltrator Steward

**Scenario:** Agent becomes steward and approves fake safe house

**Mitigation:** Requires 2 stewards. Both would need to be compromised. Independent verifications on different days reduces coordination.

### Attack: Coerced Verification

**Scenario:** Steward forced at gunpoint to verify hostile location

**Mitigation:**
- Duress PIN during verification → auto-reject + burn notice
- Buddy protocol: steward checks in after verification
- Unusual verification patterns flagged (e.g., same steward verifying 5 sanctuaries in 1 hour)

### Attack: Expired Sanctuary Compromise

**Scenario:** Sanctuary safe 3 months ago, now compromised

**Mitigation:**
- 90-day expiry forces re-verification
- Re-verification process repeats safety checks
- Expired sanctuaries automatically removed from matching

## Success Criteria

- [ ] Sanctuary resources require 2 steward verifications
- [ ] Same steward cannot verify twice
- [ ] Verifications expire after 90 days
- [ ] Critical needs only match to 3+ successful use sanctuaries
- [ ] Stewards notified of verification needs 2 weeks before expiry
- [ ] Verification status visible in steward dashboard
- [ ] All tests pass

## Migration Strategy

1. **Phase 1 (Immediate):** Deploy new tables, keep old logic working
2. **Phase 2 (Week 1):** Update API to use multi-verification for NEW sanctuaries
3. **Phase 3 (Week 2):** Migrate existing sanctuaries:
   - Mark all existing verified sanctuaries as needing 2nd verification
   - Set `first_verified_at` to original verification date
   - Set `expires_at` to 90 days from now (grace period)
   - Notify stewards to verify existing sanctuaries
4. **Phase 4 (Week 3):** Enforce strict verification rules
   - Remove sanctuaries that didn't get 2nd verification
   - Start expiring sanctuaries that hit 90 days

## Notes

This is the HIGHEST PRIORITY security improvement. Sanctuary is life-and-death. We cannot cut corners.

Multi-steward verification is standard practice for:
- Nuclear launch codes (2-person rule)
- Bank vault access (dual control)
- Classified information (need-to-know + compartmentalization)

If it's good enough for nukes, it's good enough for sanctuary.
