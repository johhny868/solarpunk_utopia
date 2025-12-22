# GAP-09: Notification/Awareness System

**Status**: ✅ FULLY IMPLEMENTED
**Implemented**: 2025-12-19 (Backend), 2025-12-21 (Frontend verified)
**Priority**: P2 - Core Experience
**Estimated Effort**: MVP 2-3 hours, Full 1-2 days
**Assigned**: Claude Agent

## Problem Statement

Alice has no way to know when proposals need her approval. She must manually navigate to /agents page and hope something's there. No notifications, no awareness, no badges.

## Current Reality

No notification system exists. Users miss important proposals.

## Required Implementation

### MVP: Polling-based Awareness (2-3 hours)

1. Backend MUST provide `/agents/proposals/pending-count` endpoint
2. Frontend MUST poll endpoint every 30 seconds
3. Frontend MUST display badge on navigation: "Agents (3)"
4. Frontend MUST show card on homepage: "3 proposals need your review"

### Full: Real-time System (1-2 days)

1. Backend MUST publish proposal events to NATS
2. Backend MUST expose WebSocket for real-time updates
3. Frontend MUST subscribe to WebSocket
4. Frontend MUST update UI immediately on new proposals

## Files to Modify

MVP:
- `app/api/agents.py` - Add pending count endpoint
- `frontend/src/components/Navigation.tsx` - Display badge
- `frontend/src/pages/HomePage.tsx` - Add proposal count card

Full:
- `app/events/proposal_publisher.py` - NATS integration
- `frontend/src/hooks/useWebSocket.ts` - WebSocket client

## Success Criteria

- [x] Users see pending proposal count - Endpoint exists at GET /agents/proposals/pending/{user_id}/count
- [x] Badge updates when proposals arrive - Navigation badge implemented with polling
- [x] No need to manually check agents page - HomePage shows pending proposals card

## Implementation Notes

**Backend (2025-12-19):**
- Endpoint: `GET /agents/proposals/pending/{user_id}/count`
- Returns: `{"user_id": "...", "pending_count": 3}`
- Located in: `app/api/agents.py` lines 120-132

**Frontend (Verified 2025-12-21):**
- ✅ `usePendingCount` hook in `frontend/src/hooks/useAgents.ts` (line 117-123)
- ✅ Polls endpoint every 30 seconds using `refetchInterval: 30000`
- ✅ Navigation badge in `frontend/src/components/Navigation.tsx` (lines 67-71, 112-116)
- ✅ Shows red badge with count on "AI Agents" nav item
- ✅ HomePage displays "AI Proposals Pending Review" section (lines 138-157)
- ✅ Shows up to 3 pending proposals with link to view all

**Reference**: `VISION_REALITY_DELTA.md:GAP-09`
