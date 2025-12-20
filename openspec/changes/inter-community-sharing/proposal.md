# Proposal: Inter-Community Sharing (Peer-to-Peer)

**Submitted By:** Community Request
**Date:** 2025-12-19
**Status:** NEW
**Priority:** P2 - First Month
**Depends On:** GAP-03 (Community Entity)

## Problem Statement

Communities are currently isolated. Resources can't flow where they're needed across community boundaries.

## Design Principles

**No gatekeepers.** Individuals decide what to share, not stewards.

**Consent-based.** You choose your visibility, others choose what they see.

**Emergent connections.** Relationships form organically, not through approval flows.

**Federation over hierarchy.** Communities are peers, not parent/child.

## Proposed Solution: Individual Choice Model

### Core Concept: You Control Your Visibility

Every person chooses their own sharing radius:

```python
class SharingPreference(BaseModel):
    """Individual controls their own visibility"""
    user_id: str

    # Who can see my offers/needs?
    visibility: Literal[
        "my_cell",           # Only my immediate cell (5-50 people)
        "my_community",      # My whole community
        "trusted_network",   # Anyone I trust >= 0.5
        "anyone_local",      # Anyone within X km
        "network_wide",      # The whole mesh
    ] = "my_community"

    # Optional location fuzzing for privacy
    location_precision: Literal["exact", "neighborhood", "city", "region"] = "neighborhood"
```

No steward approval. No partnership ceremonies. Just: "I'm willing to share this widely."

### Discovery: Pull, Not Push

Instead of communities "partnering" and pushing listings at each other, individuals browse and pull what interests them:

```python
@router.get("/discover")
async def discover_resources(
    current_user=Depends(get_current_user),
    resource_type: Optional[str] = None,
    max_distance_km: Optional[float] = 50,
    min_trust: float = 0.3,  # Only see people with some trust connection
):
    """
    Discover resources from people who've chosen to share widely.

    This is a PULL model - you browse what's available.
    Creators chose to make things visible. You choose what to look at.
    """
    # Find resources from people who:
    # 1. Chose visibility that includes you
    # 2. You have minimum trust connection to
    # 3. Are within your distance preference

    visible_resources = await find_visible_to_user(
        viewer=current_user,
        min_trust=min_trust,
        max_distance=max_distance_km,
        resource_type=resource_type,
    )

    return visible_resources
```

### Trust as the Connective Tissue

Instead of institutional partnerships, trust relationships create organic bridges:

```
Alice (Downtown) trusts Bob (Eastside) → trust 0.7
Bob vouched for Carol → Carol has 0.56 trust from Alice's perspective

If Carol shares "network_wide", Alice can discover Carol's offers
because there's a trust path.
```

No community-level decisions. The web of trust IS the federation.

```python
async def can_see_resource(viewer_id: str, resource: Resource) -> bool:
    """Can this viewer see this resource?"""

    creator = resource.creator_id
    visibility = await get_sharing_preference(creator)

    if visibility.visibility == "my_cell":
        return await same_cell(viewer_id, creator)

    elif visibility.visibility == "my_community":
        return await same_community(viewer_id, creator)

    elif visibility.visibility == "trusted_network":
        trust = await compute_trust_between(viewer_id, creator)
        return trust >= 0.5

    elif visibility.visibility == "anyone_local":
        distance = await distance_between(viewer_id, creator)
        return distance <= visibility.local_radius_km

    elif visibility.visibility == "network_wide":
        # Still require SOME trust connection to prevent pure strangers
        trust = await compute_trust_between(viewer_id, creator)
        return trust >= 0.1  # Very loose - just need to be in the web somewhere

    return False
```

### Cross-Community Exchange

When someone from another community responds to your offer, the exchange just... happens. No special handling needed.

```python
class Exchange(BaseModel):
    provider_id: str
    receiver_id: str
    resource_id: str

    # Track for metrics, not for permission
    provider_community: Optional[str]
    receiver_community: Optional[str]

    @property
    def is_cross_community(self) -> bool:
        return (
            self.provider_community
            and self.receiver_community
            and self.provider_community != self.receiver_community
        )
```

The metric is interesting ("look, resources are flowing between communities!") but it's not a gate.

### UI: Simple Preference

When creating an offer:

```
Who can see this?

○ Just my cell (the people I know directly)
○ My community
● Anyone I'm connected to through trust [DEFAULT]
○ Anyone nearby (within 25km)
○ Everyone on the network
```

When browsing:

```
Discover Resources

[Search: ___________]

Filters:
  Distance: [Within 50km ▾]
  Trust: [Any connection ▾]

Results:
  🥬 Fresh vegetables - 2km away (trusted friend of friend)
  🔧 Tool lending - 8km away (in your extended network)
  🚗 Ride share - 15km away (community member)
```

### What About Bad Actors?

The trust system handles this:

- No trust path to you = can't see your stuff
- Low trust = limited visibility
- Revoked trust = cascading visibility loss
- Block list = invisible to each other regardless of visibility settings

```python
async def find_visible_to_user(viewer, ...):
    resources = await get_broadly_shared_resources(...)

    # Filter out blocked users (bidirectional)
    blocked = await get_blocked_users(viewer.id)
    resources = [r for r in resources if r.creator_id not in blocked]

    # Filter to only those with trust path
    visible = []
    for resource in resources:
        trust = await compute_trust_between(viewer.id, resource.creator_id)
        if trust >= min_trust:
            visible.append(resource)

    return visible
```

### No "Partnership" Concept

Communities don't "partner." People connect.

If many people in Community A trust many people in Community B, resources will naturally flow between them. If the trust isn't there, they won't.

This is emergent federation, not negotiated treaties.

## Database Changes

```sql
-- Individual sharing preferences
CREATE TABLE sharing_preferences (
    user_id TEXT PRIMARY KEY,
    visibility TEXT DEFAULT 'my_community',
    location_precision TEXT DEFAULT 'neighborhood',
    local_radius_km REAL DEFAULT 25,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track cross-community for metrics only
ALTER TABLE exchanges ADD COLUMN provider_community_id TEXT;
ALTER TABLE exchanges ADD COLUMN receiver_community_id TEXT;
```

## Requirements

### SHALL
- SHALL let individuals choose their own visibility
- SHALL use trust paths for cross-community discovery
- SHALL NOT require steward/admin approval for sharing
- SHALL respect block lists across communities

### SHALL NOT
- SHALL NOT have "partnership" as a concept
- SHALL NOT require community-level decisions for individual sharing
- SHALL NOT expose people to those with no trust connection

## Success Criteria

- [ ] Users can set their sharing preference
- [ ] Discovery shows resources based on trust + visibility
- [ ] Cross-community exchanges tracked for metrics
- [ ] No approval workflows anywhere
- [ ] Block lists respected network-wide
- [ ] Resources flow organically based on trust

## Philosophical Alignment

> "No one should have to ask permission to share." - Kropotkin perspective

> "The gift moves on its own." - Lewis Hyde

The network is the federation. Trust is the protocol. No kings, no gatekeepers.
