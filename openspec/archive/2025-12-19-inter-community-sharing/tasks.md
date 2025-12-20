# Inter-Community Sharing - Implementation Tasks

## Phase 1: Public Listings (P1 - Quick Win)

### Backend
- [ ] Add `is_public` field to Listing model
- [ ] Create database migration for is_public column
- [ ] Add `get_public_listings()` to ListingRepository
- [ ] Update `GET /listings` to accept `include_public` query param
- [ ] Add index on (is_public, status) for performance
- [ ] Update listing creation to accept is_public flag

### Frontend
- [ ] Add "Make visible to other communities" checkbox to offer/need forms
- [ ] Add visual indicator for public listings in list view
- [ ] Add toggle filter for "Include public from other communities"
- [ ] Show community name on cross-community listings

### Testing
- [ ] Test public listing visibility across communities
- [ ] Test default is community-only
- [ ] Test listing creation with is_public flag

## Phase 2: Community Partnerships (P2)

### Backend
- [ ] Create CommunityPartnership model
- [ ] Create community_partnerships database table
- [ ] Create PartnershipRepository with CRUD operations
- [ ] Create `/partnerships/propose` endpoint
- [ ] Create `/partnerships/{id}/approve` endpoint
- [ ] Create `/partnerships/{id}/dissolve` endpoint
- [ ] Add `get_active_for_community()` query
- [ ] Update listing query to include partner listings

### Frontend
- [ ] Add "Partnerships" section to Steward Dashboard
- [ ] Create "Propose Partnership" flow
- [ ] Create "Approve Partnership" notification + action
- [ ] Show partner community listings with visual distinction
- [ ] Add partner filter to listing views

### Testing
- [ ] Test partnership proposal flow
- [ ] Test bilateral approval requirement
- [ ] Test partner listing visibility
- [ ] Test partnership dissolution

## Phase 3: Network Discovery (P2)

### Backend
- [ ] Create `/discovery/communities` endpoint
- [ ] Create `/discovery/browse` endpoint for network-wide search
- [ ] Add public offer/need counts to community profiles
- [ ] Add location-based filtering to browse

### Frontend
- [ ] Create "Browse Network" page
- [ ] Show community cards with public listing counts
- [ ] Implement resource type filtering
- [ ] Implement location radius filtering
- [ ] Add "Request Partnership" action from discovery

### Testing
- [ ] Test community discovery endpoint
- [ ] Test network browse with filters
- [ ] Test location-based discovery

## Phase 4: Cross-Community Exchange Tracking (P3)

### Backend
- [ ] Add community ID fields to Exchange model
- [ ] Create database migration for community tracking
- [ ] Add `get_cross_community_exchanges()` query
- [ ] Add cross-community flow metrics to leakage service
- [ ] Update exchange creation to capture community IDs

### Frontend
- [ ] Show cross-community indicator on exchanges
- [ ] Add cross-community metrics to dashboard
- [ ] Create community flow visualization

### Testing
- [ ] Test cross-community exchange detection
- [ ] Test flow metrics calculation

## Definition of Done

- [ ] All tests passing
- [ ] API documentation updated
- [ ] Frontend components styled consistently
- [ ] Default behavior unchanged (community isolation)
- [ ] Steward approval required for partnerships
- [ ] Privacy maintained for non-public listings
