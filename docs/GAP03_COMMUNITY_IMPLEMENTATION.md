# GAP-03: Community/Commune Entity - Implementation Summary

**Status**: Partially Complete (Backend Complete, Frontend In Progress)
**Date**: December 19, 2025

## Overview

GAP-03 adds multi-community support to the Solarpunk app, allowing multiple communes to coexist on a single server. Each community has its own members, listings, matches, and exchanges.

## Completed Work

### Backend (✅ Complete)

#### 1. Database Schema

**New Tables:**
- `communities` - Community information (id, name, description, settings, is_public)
- `community_memberships` - User-to-community relationships with roles (creator, admin, member)

**Schema Updates:**
- Added `community_id` column to:
  - `listings` (offers/needs)
  - `matches`
  - `exchanges`
  - `proposals`
- Created indexes for efficient community-scoped queries

**Files:**
- `app/database/db.py` - Added communities and community_memberships tables
- `valueflows_node/app/database/vf_schema.sql` - Added community_id to VF tables
- `valueflows_node/app/database/migrations/002_add_community_id.sql` - Migration script

#### 2. Backend Models

**New Models:**
- `Community` - Community data model
- `CommunityCreate` - Community creation request
- `CommunityUpdate` - Community update request
- `CommunityMembership` - Membership data model
- `CommunityMembershipCreate` - Membership creation request
- `CommunityStats` - Community statistics (member count, listing count, etc.)

**Model Updates:**
- Added `community_id: Optional[str]` to:
  - `Listing` (valueflows_node/app/models/vf/listing.py)
  - `Match` (valueflows_node/app/models/vf/match.py)
  - `Exchange` (valueflows_node/app/models/vf/exchange.py)
- Updated `to_dict()` and `from_dict()` methods to include community_id

**Files:**
- `valueflows_node/app/models/community.py` - Community models

#### 3. Backend Services

Created `CommunityService` with methods:
- `create_community()` - Create new community, add creator as first member
- `get_community()` - Get community by ID
- `get_user_communities()` - Get all communities a user belongs to
- `update_community()` - Update community settings
- `delete_community()` - Delete community (creator only)
- `add_member()` - Add user to community
- `get_members()` - List all community members
- `remove_member()` - Remove user from community
- `is_member()` - Check membership
- `get_member_role()` - Get user's role in community
- `get_stats()` - Get community statistics

**Files:**
- `valueflows_node/app/services/community_service.py`

#### 4. API Endpoints

**Routes: `/communities`**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/communities` | Create new community | ✅ |
| GET | `/communities` | List user's communities | ✅ |
| GET | `/communities/{id}` | Get community details | ✅ (member or public) |
| PATCH | `/communities/{id}` | Update community | ✅ (admin/creator) |
| DELETE | `/communities/{id}` | Delete community | ✅ (creator only) |
| POST | `/communities/{id}/members` | Add member | ✅ (admin/creator) |
| GET | `/communities/{id}/members` | List members | ✅ (member or public) |
| DELETE | `/communities/{id}/members/{uid}` | Remove member | ✅ (admin/creator or self) |
| GET | `/communities/{id}/stats` | Community stats | ✅ (member or public) |

**Permissions:**
- **Creator**: Can update settings, add/remove members, delete community
- **Admin**: Can update settings, add/remove members
- **Member**: Can view, participate, remove self
- **Public communities**: Non-members can view details

**Files:**
- `valueflows_node/app/api/communities.py` - Community API endpoints
- `valueflows_node/app/main.py` - Registered communities router

### Frontend (🚧 Partial)

#### 1. Community Context

Created React Context to manage community state:
- `currentCommunity` - Currently selected community
- `communities` - List of user's communities
- `selectCommunity(id)` - Switch active community
- `refreshCommunities()` - Reload communities list
- `createCommunity(name, description)` - Create new community

**Persistence:**
- Selected community saved to `localStorage` (key: `solarpunk_current_community`)
- Auto-restores on page reload
- Auto-selects first community if none selected

**Files:**
- `frontend/src/contexts/CommunityContext.tsx` - Community React Context
- `frontend/src/App.tsx` - Wrapped with CommunityProvider

## Remaining Work

### Frontend Tasks

1. **CommunitySelector Component** (Pending)
   - Dropdown to switch between communities
   - Display current community name
   - "Create Community" option

2. **Update API Calls** (Pending)
   - Add `community_id` parameter to all listing/match/exchange API calls
   - Filter by `currentCommunity.id` in all queries

3. **Communities Management Page** (Pending)
   - View community details
   - Manage members (add/remove)
   - Update community settings
   - Leave community

### Backend Tasks

1. **Update Repositories** (Pending)
   - Modify listing/match/exchange repositories to filter by community_id
   - Update find/create methods to require community_id

2. **Update Agents** (Pending)
   - Scope agent operations to specific community
   - Pass community_id when creating proposals/matches

### Testing

- [ ] Create community via API
- [ ] Add members to community
- [ ] Create listings scoped to community
- [ ] Verify data isolation between communities
- [ ] Test frontend community switching
- [ ] Test permissions (creator/admin/member)

## Migration Strategy

For existing data:

1. Create default community: "Default Commune"
2. Migrate all existing data to default community
3. Update all existing user memberships to default community
4. Users can then create new communities or rename default

## API Examples

### Create Community

```bash
POST /api/vf/communities
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Oak Street Collective",
  "description": "Community garden and tool library",
  "is_public": true
}
```

### List User's Communities

```bash
GET /api/vf/communities
Authorization: Bearer <token>
```

### Add Member

```bash
POST /api/vf/communities/{community_id}/members
Authorization: Bearer <token>
Content-Type: application/json

{
  "user_id": "user:abc123",
  "role": "member"
}
```

## Database Schema

### communities

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| name | TEXT | Community name (unique) |
| description | TEXT | Optional description |
| created_at | TEXT | ISO 8601 timestamp |
| settings | TEXT | JSON settings blob |
| is_public | INTEGER | 1 if public, 0 if private |

### community_memberships

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Primary key |
| user_id | TEXT | Foreign key to users |
| community_id | TEXT | Foreign key to communities |
| role | TEXT | creator, admin, or member |
| joined_at | TEXT | ISO 8601 timestamp |

**Unique constraint:** (user_id, community_id)

## Files Modified/Created

### Backend
- `valueflows_node/app/models/community.py` ✅ (new)
- `valueflows_node/app/services/community_service.py` ✅ (new)
- `valueflows_node/app/api/communities.py` ✅ (new)
- `valueflows_node/app/main.py` ✅ (modified)
- `valueflows_node/app/database/vf_schema.sql` ✅ (modified)
- `valueflows_node/app/database/migrations/002_add_community_id.sql` ✅ (new)
- `app/database/db.py` ✅ (modified)
- `valueflows_node/app/models/vf/listing.py` ✅ (modified)
- `valueflows_node/app/models/vf/match.py` ✅ (modified)
- `valueflows_node/app/models/vf/exchange.py` ✅ (modified)

### Frontend
- `frontend/src/contexts/CommunityContext.tsx` ✅ (new)
- `frontend/src/App.tsx` ✅ (modified)

## Next Steps

1. Create `CommunitySelector` component for UI
2. Update all API calls to include community filtering
3. Create Communities management page
4. Test multi-community scenarios
5. Update GAP-03 proposal status to Complete

## Related

- **GAP-02**: User Identity System (dependency - completed)
- **GAP-17**: "My Stuff" View (will benefit from community filtering)
