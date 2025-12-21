# GAP-42: No Authentication System (SECURITY)

**Status**: ✅ IMPLEMENTED
**Priority**: P6 - Production/Security
**Severity**: CRITICAL
**Estimated Effort**: See GAP-02
**Assigned**: Claude Agent
**Completed**: December 19, 2025

## Problem Statement

APIs accept `user_id` as query parameter with no verification. Anyone can impersonate anyone by changing the URL.

**This is a duplicate/related to GAP-02 (User Identity System).**

## Current Reality

**Locations**:
- `app/api/agents.py:79` - user_id from query, no verification
- `valueflows_node/app/api/vf/listings.py:26` - no auth check
- `frontend/src/api/agents.ts:79` - hardcoded 'demo-user'

Example vulnerability:
```bash
# Alice's offers
curl http://localhost:8001/vf/listings?user_id=alice

# Bob can see Alice's data by changing URL
curl http://localhost:8001/vf/listings?user_id=alice

# Bob can CREATE as Alice!
curl -X POST http://localhost:8001/vf/listings/ \
  -d '{"agent_id": "alice", "listing_type": "offer", ...}'
```

## Relationship to GAP-02

**This gap is addressed by GAP-02 (User Identity System).**

GAP-02 provides:
- JWT or session-based authentication
- Middleware to verify identity
- User registration/login flow
- Request-scoped user context

Once GAP-02 is implemented:
- `user_id` comes from authenticated session (not query params)
- Middleware blocks unauthenticated requests
- Users can only act as themselves

## Additional Requirements (Beyond GAP-02)

### MUST Requirements

1. System MUST remove all `user_id` query parameters
2. System MUST extract user from `request.state.user` only
3. System MUST return 401 for unauthenticated requests
4. System MUST return 403 for authorization violations
5. System MUST log authentication failures

### SHOULD Requirements

1. System SHOULD implement rate limiting on auth endpoints (ephemeral, per-IP, not stored)
2. System SHOULD use in-memory rate limiting for failed attempts (no persistent tracking of "who failed when")
3. System SHOULD support API keys for service-to-service auth

**Privacy Note:** We do NOT track failed login attempts per-user. Rate limiting is ephemeral, in-memory, and IP-based only. No historical record of "who tried to login and failed" is kept.

## Success Criteria

- [x] No endpoints accept `user_id` as parameter
- [x] All protected endpoints require authentication
- [x] Users cannot impersonate others
- [x] GAP-02 proposal is implemented

## Implementation Notes

All agent API endpoints have been updated to use the authentication middleware:
- `GET /agents/proposals` - Uses `get_current_user` for optional auth
- `GET /agents/proposals/pending` - Now requires auth via `require_auth`
- `GET /agents/proposals/pending/count` - Now requires auth via `require_auth`
- `POST /agents/proposals/{id}/approve` - Already had `require_auth`
- `POST /agents/proposals/{id}/reject` - Already had `require_auth`

User identity now comes from the authenticated session token, not from untrusted query parameters.

## References

- **See**: `openspec/changes/gap-02-user-identity-system/` for full implementation
- Original spec: `VISION_REALITY_DELTA.md:GAP-42`
- OWASP: https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication
