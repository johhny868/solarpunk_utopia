# Proposal: Inter-Community Sharing

**Submitted By:** Community Request
**Date:** 2025-12-19
**Status:** NEW
**Priority:** P2 - First Month
**Depends On:** GAP-03 (Community Entity)

## Problem Statement

Communities are currently isolated by design - each community only sees its own offers, needs, and exchanges. While this data scoping is intentional and valuable for privacy, there's no mechanism for cross-community sharing when desired.

A network of isolated communities cannot achieve the scale needed for economic withdrawal. If Alice in the "Downtown Mutual Aid" community has excess vegetables but no one in her community needs them, those vegetables rot - even though Bob in "Eastside Collective" desperately needs vegetables.

**The gift economy should flow across community boundaries.**

## Current State

- ✅ Communities are isolated (each sees only their own data)
- ✅ Data scoping works correctly per-community
- ❌ No mechanism for cross-community sharing
- ❌ No way to discover resources in other communities
- ❌ No cross-community exchange tracking

## Proposed Solution: Phased Approach

### Phase 1: Public Listings (Quick Win)

Add `is_public` flag to listings for opt-in visibility across communities.

```python
# app/models/listing.py
class Listing(BaseModel):
    id: str
    type: Literal["offer", "need"]
    agent_id: str
    community_id: Optional[str] = None

    # NEW: Cross-community visibility
    is_public: bool = False  # Default to community-only

    # Existing fields...
    resource_specification_id: str
    quantity: float
    description: str
    location: Optional[Location] = None
    created_at: datetime
    expires_at: Optional[datetime] = None
```

```python
# app/api/listings.py
@router.get("/", response_model=List[Listing])
async def get_listings(
    community_id: Optional[str] = None,
    include_public: bool = False,  # NEW: opt-in to see public listings
    current_user=Depends(get_current_user),
    repo: ListingRepository = Depends(get_listing_repo),
):
    """Get listings with optional cross-community visibility"""

    # Get user's community listings
    listings = await repo.get_by_community(community_id or current_user.community_id)

    # Optionally include public listings from other communities
    if include_public:
        public_listings = await repo.get_public_listings(
            exclude_community=community_id or current_user.community_id
        )
        listings.extend(public_listings)

    return listings
```

```python
# app/database/listing_repository.py
class ListingRepository:
    async def get_public_listings(
        self,
        exclude_community: str = None,
        limit: int = 100,
    ) -> List[Listing]:
        """Get all public listings, optionally excluding a community"""
        query = """
            SELECT * FROM listings
            WHERE is_public = true
            AND status = 'active'
            AND (expires_at IS NULL OR expires_at > ?)
        """
        params = [datetime.utcnow()]

        if exclude_community:
            query += " AND community_id != ?"
            params.append(exclude_community)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        return await self.db.fetch_all(query, params)
```

### Phase 2: Community Partnerships

Allow communities to explicitly partner for bilateral sharing.

```python
# app/models/community_partnership.py
class CommunityPartnership(BaseModel):
    """Bilateral partnership between two communities"""
    id: str
    community_a_id: str
    community_b_id: str

    # What's shared
    share_offers: bool = True
    share_needs: bool = True
    share_member_count: bool = False  # Privacy option

    # Governance
    proposed_by: str  # User ID
    approved_by_a: Optional[str] = None  # Steward from A
    approved_by_b: Optional[str] = None  # Steward from B

    status: Literal["proposed", "active", "dissolved"] = "proposed"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def is_active(self) -> bool:
        return (
            self.status == "active"
            and self.approved_by_a is not None
            and self.approved_by_b is not None
        )
```

```python
# app/api/partnerships.py
@router.post("/propose")
async def propose_partnership(
    request: ProposePartnershipRequest,
    current_user=Depends(get_current_user),
    repo: PartnershipRepository = Depends(get_partnership_repo),
):
    """Propose a partnership with another community"""

    # Verify proposer is steward of their community
    if not await is_steward(current_user.id, request.from_community_id):
        raise HTTPException(403, "Only stewards can propose partnerships")

    partnership = CommunityPartnership(
        id=str(uuid4()),
        community_a_id=request.from_community_id,
        community_b_id=request.to_community_id,
        proposed_by=current_user.id,
        approved_by_a=current_user.id,  # Proposer auto-approves for their side
    )

    await repo.create(partnership)

    # Notify stewards of target community
    await notify_stewards(
        request.to_community_id,
        f"Partnership proposed from {request.from_community_name}"
    )

    return partnership


@router.post("/{partnership_id}/approve")
async def approve_partnership(
    partnership_id: str,
    current_user=Depends(get_current_user),
    repo: PartnershipRepository = Depends(get_partnership_repo),
):
    """Approve a partnership (steward of receiving community)"""

    partnership = await repo.get(partnership_id)
    if not partnership:
        raise HTTPException(404, "Partnership not found")

    # Determine which side the approver is on
    if await is_steward(current_user.id, partnership.community_b_id):
        partnership.approved_by_b = current_user.id
    elif await is_steward(current_user.id, partnership.community_a_id):
        partnership.approved_by_a = current_user.id
    else:
        raise HTTPException(403, "Only stewards of partner communities can approve")

    # Check if fully approved
    if partnership.approved_by_a and partnership.approved_by_b:
        partnership.status = "active"

    await repo.update(partnership)
    return partnership
```

```python
# Updated listing query with partnerships
async def get_listings_with_partnerships(
    community_id: str,
    include_public: bool = False,
    include_partners: bool = True,  # NEW
    repo: ListingRepository,
    partnership_repo: PartnershipRepository,
) -> List[Listing]:
    """Get listings including partner community listings"""

    # Own community
    listings = await repo.get_by_community(community_id)

    # Partner communities
    if include_partners:
        partnerships = await partnership_repo.get_active_for_community(community_id)
        for partnership in partnerships:
            partner_id = (
                partnership.community_b_id
                if partnership.community_a_id == community_id
                else partnership.community_a_id
            )
            partner_listings = await repo.get_by_community(partner_id)

            # Mark as from partner community
            for listing in partner_listings:
                listing.from_partner_community = True

            listings.extend(partner_listings)

    # Public listings from non-partner communities
    if include_public:
        partner_ids = [p.community_a_id for p in partnerships] + [p.community_b_id for p in partnerships]
        public_listings = await repo.get_public_listings(
            exclude_communities=[community_id] + partner_ids
        )
        listings.extend(public_listings)

    return listings
```

### Phase 3: Discovery Mode

Add a "Browse All Communities" view for discovering resources network-wide.

```python
# app/api/discovery.py
@router.get("/communities")
async def discover_communities(
    current_user=Depends(get_current_user),
    repo: CommunityRepository = Depends(get_community_repo),
):
    """Discover communities in the network"""
    communities = await repo.get_discoverable()

    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "member_count": c.member_count if c.show_member_count else None,
            "active_offers": await repo.count_public_offers(c.id),
            "active_needs": await repo.count_public_needs(c.id),
            "is_partner": await partnership_repo.are_partners(
                current_user.community_id, c.id
            ),
        }
        for c in communities
    ]


@router.get("/browse")
async def browse_network(
    resource_type: Optional[str] = None,
    location_radius_km: Optional[float] = None,
    current_user=Depends(get_current_user),
    repo: ListingRepository = Depends(get_listing_repo),
):
    """Browse public listings across the entire network"""

    listings = await repo.get_public_listings(
        resource_type=resource_type,
        near_location=current_user.location if location_radius_km else None,
        radius_km=location_radius_km,
    )

    # Group by community for display
    by_community = defaultdict(list)
    for listing in listings:
        by_community[listing.community_id].append(listing)

    return {
        "total_listings": len(listings),
        "communities": len(by_community),
        "by_community": dict(by_community),
    }
```

### Phase 4: Cross-Community Exchanges (Future)

Track exchanges that span community boundaries.

```python
# app/models/exchange.py
class Exchange(BaseModel):
    # ... existing fields ...

    # Cross-community tracking
    provider_community_id: str
    receiver_community_id: str
    is_cross_community: bool = False

    @property
    def is_cross_community(self) -> bool:
        return self.provider_community_id != self.receiver_community_id
```

```python
# app/services/leakage_metrics_service.py
async def compute_cross_community_flow(self) -> Dict:
    """Track value flowing between communities"""

    cross_exchanges = await self.exchange_repo.get_cross_community_exchanges(
        since=datetime.utcnow() - timedelta(days=30)
    )

    flows = defaultdict(lambda: {"outflow": 0, "inflow": 0})

    for exchange in cross_exchanges:
        flows[exchange.provider_community_id]["outflow"] += exchange.estimated_value
        flows[exchange.receiver_community_id]["inflow"] += exchange.estimated_value

    return {
        "total_cross_community_value": sum(e.estimated_value for e in cross_exchanges),
        "exchange_count": len(cross_exchanges),
        "community_flows": dict(flows),
    }
```

## UI Considerations

### Listing Creation
```
[ ] Make this offer visible to other communities

When checked:
- Offer appears in partner community feeds
- Offer appears in network-wide browse
- Your community name is visible
```

### Listing Display
```
🏠 Downtown Mutual Aid (your community)
├── 🥬 Fresh vegetables - 5 lbs
├── 🔧 Tool lending - drill, saw
└── 📚 Book exchange - fiction

🤝 Eastside Collective (partner)
├── 🍞 Fresh bread - weekly
└── 🧵 Clothing repair

🌐 Network (public)
├── 🚗 Ride share - downtown area
└── 🏡 Space for events
```

### Partnership Management (Steward Dashboard)
```
Community Partnerships
──────────────────────
Active:
  ✅ Eastside Collective (since Dec 2024)
  ✅ Northside Co-op (since Nov 2024)

Pending:
  ⏳ Westside Mutual Aid (awaiting their approval)

Incoming:
  📨 Southside Network wants to partner
     [Approve] [Decline] [View Community]
```

## Requirements

### SHALL Requirements
- SHALL allow listings to be marked as public (visible network-wide)
- SHALL default to community-only visibility (is_public = false)
- SHALL allow communities to form bilateral partnerships
- SHALL require steward approval from both communities for partnerships
- SHALL allow browsing public listings across the network
- SHALL track cross-community exchanges separately

### SHOULD Requirements
- SHOULD show community origin for cross-community listings
- SHOULD allow filtering by own/partner/public listings
- SHOULD display partnership status in community profiles

### MUST Requirements
- MUST NOT expose private listings to other communities
- MUST NOT allow partnerships without steward consent
- MUST maintain community isolation as default

## Database Migrations

```sql
-- Add is_public to listings
ALTER TABLE listings ADD COLUMN is_public BOOLEAN DEFAULT FALSE;
CREATE INDEX idx_listings_public ON listings(is_public, status);

-- Community partnerships table
CREATE TABLE community_partnerships (
    id TEXT PRIMARY KEY,
    community_a_id TEXT NOT NULL,
    community_b_id TEXT NOT NULL,
    share_offers BOOLEAN DEFAULT TRUE,
    share_needs BOOLEAN DEFAULT TRUE,
    share_member_count BOOLEAN DEFAULT FALSE,
    proposed_by TEXT NOT NULL,
    approved_by_a TEXT,
    approved_by_b TEXT,
    status TEXT DEFAULT 'proposed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dissolved_at TIMESTAMP,
    FOREIGN KEY (community_a_id) REFERENCES communities(id),
    FOREIGN KEY (community_b_id) REFERENCES communities(id),
    UNIQUE(community_a_id, community_b_id)
);
CREATE INDEX idx_partnerships_status ON community_partnerships(status);

-- Cross-community exchange tracking
ALTER TABLE exchanges ADD COLUMN provider_community_id TEXT;
ALTER TABLE exchanges ADD COLUMN receiver_community_id TEXT;
CREATE INDEX idx_exchanges_cross ON exchanges(provider_community_id, receiver_community_id);
```

## Testing

```python
def test_public_listing_visibility():
    """Public listings visible across communities"""
    community_a = create_community()
    community_b = create_community()

    # Create public listing in A
    listing = create_listing(community_a, is_public=True)

    # Should be visible from B with include_public=True
    listings = get_listings(community_b, include_public=True)
    assert listing.id in [l.id for l in listings]

    # Should NOT be visible without include_public
    listings = get_listings(community_b, include_public=False)
    assert listing.id not in [l.id for l in listings]


def test_partnership_requires_both_approvals():
    """Partnerships require steward approval from both sides"""
    community_a = create_community()
    community_b = create_community()
    steward_a = create_steward(community_a)
    steward_b = create_steward(community_b)

    # Propose partnership
    partnership = propose_partnership(community_a, community_b, steward_a)
    assert partnership.status == "proposed"

    # Only A approved
    assert partnership.approved_by_a == steward_a.id
    assert partnership.approved_by_b is None

    # B approves
    approve_partnership(partnership.id, steward_b)
    partnership = get_partnership(partnership.id)

    assert partnership.status == "active"
    assert partnership.approved_by_b == steward_b.id


def test_partner_listings_visible():
    """Partner community listings visible to each other"""
    community_a = create_community()
    community_b = create_community()
    create_active_partnership(community_a, community_b)

    # Create listing in A (not public)
    listing = create_listing(community_a, is_public=False)

    # Should be visible from B (partner)
    listings = get_listings(community_b, include_partners=True)
    assert listing.id in [l.id for l in listings]

    # Should NOT be visible from C (not partner)
    community_c = create_community()
    listings = get_listings(community_c, include_partners=True)
    assert listing.id not in [l.id for l in listings]
```

## Files to Create/Modify

1. `app/models/listing.py` - Add is_public field
2. `app/database/listing_repository.py` - Add public listing queries
3. `app/api/listings.py` - Add include_public parameter
4. New: `app/models/community_partnership.py`
5. New: `app/database/partnership_repository.py`
6. New: `app/api/partnerships.py`
7. New: `app/api/discovery.py`
8. `app/models/exchange.py` - Add cross-community tracking
9. `app/services/leakage_metrics_service.py` - Add cross-community metrics

## Effort Estimate

| Phase | Effort | Priority |
|-------|--------|----------|
| Phase 1: Public Listings | 2 hours | P1 |
| Phase 2: Partnerships | 4 hours | P2 |
| Phase 3: Discovery | 2 hours | P2 |
| Phase 4: Cross-Community Tracking | 2 hours | P3 |
| Testing | 2 hours | - |
| **Total** | **12 hours** | - |

## Success Criteria

- [ ] Listings can be marked as public
- [ ] Public listings visible network-wide with opt-in
- [ ] Communities can form partnerships
- [ ] Partnership requires bilateral steward approval
- [ ] Partner listings visible to each other
- [ ] Network discovery browse works
- [ ] Cross-community exchanges tracked
- [ ] Community isolation remains default

## Philosophical Alignment

From the Philosopher Council reviews:

> "The revolution cannot be contained in one neighborhood." - Emma Goldman perspective

This feature enables:
- **Mutual aid at scale** - Resources flow where needed, not just where located
- **Solidarity networks** - Communities support each other
- **Economic withdrawal** - Larger coordinated impact on extractive systems
- **Resilience** - If one community is disrupted, others can help

While maintaining:
- **Local autonomy** - Communities control their visibility
- **Consent-based sharing** - No forced exposure
- **Privacy by default** - Must opt-in to share
