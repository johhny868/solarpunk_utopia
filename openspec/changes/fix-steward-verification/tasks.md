# Fix Steward Verification - Tasks

## Task Breakdown

### Phase 1: Create Infrastructure (30 minutes)

- [ ] Create `app/api/dependencies/steward.py` with `require_steward` dependency
- [ ] Add STEWARD_TRUST_THRESHOLD to config (default 0.9)
- [ ] Add logging for security audit trail
- [ ] Create `tests/test_steward_verification.py`

### Phase 2: Apply to Mycelial Strike (15 minutes)

- [ ] Update `app/api/mycelial_strike.py:284` - override_strike endpoint
- [ ] Update `app/api/mycelial_strike.py:314` - whitelist_user endpoint
- [ ] Remove TODO comments after applying dependency

### Phase 3: Apply to Saturnalia (15 minutes)

- [ ] Update `app/api/saturnalia.py:146` - create_event endpoint
- [ ] Update `app/api/saturnalia.py:184` - update_event endpoint
- [ ] Update `app/api/saturnalia.py:282` - create_config endpoint
- [ ] Update `app/api/saturnalia.py:306` - update_config endpoint
- [ ] Remove TODO comments

### Phase 4: Apply to Ancestor Voting (15 minutes)

- [ ] Update `app/api/ancestor_voting.py:149` - create_memorial_fund endpoint
- [ ] Update `app/api/ancestor_voting.py:282` - update_memorial_fund endpoint
- [ ] Update `app/api/ancestor_voting.py:328` - request_removal endpoint
- [ ] Update `app/api/ancestor_voting.py:390` - allocate_weight endpoint
- [ ] Remove TODO comments

### Phase 5: Apply to Economic Withdrawal (15 minutes)

- [ ] Update `app/api/economic_withdrawal.py:240` - update_campaign endpoint
- [ ] Update `app/api/economic_withdrawal.py:387` - create_bulk_buy endpoint
- [ ] Update `app/api/economic_withdrawal.py:473` - create_alternative endpoint
- [ ] Remove TODO comments

### Phase 6: Apply to Remaining Endpoints (15 minutes)

- [ ] Update `app/api/sanctuary.py:167` - verify_safe_house endpoint
- [ ] Update `app/api/resilience_metrics.py:334` - get_cell_trends endpoint
- [ ] Remove TODO comments

### Phase 7: Validation (30 minutes)

- [ ] Run `pytest tests/test_steward_verification.py -v`
- [ ] Run `pytest tests/test_api_endpoints.py -v` (no regression)
- [ ] Run full test suite
- [ ] Manual testing with real trust scores

---

## Estimated Time: 2 hours

## Dependencies

- WebOfTrustService must be working (verified in GAP-118 fix)
- Authentication system must be working

## Risk Assessment

- **Low risk**: This is adding restrictions, not removing them
- **Breaking change**: Users with trust < 0.9 will lose access to these endpoints
- **Mitigation**: This is the intended behavior per FRAUD_ABUSE_SAFETY.md
