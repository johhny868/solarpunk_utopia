"""
Discovery API - Cross-community resource discovery

Implements the "pull, not push" model for inter-community sharing.
Individuals control their visibility. You browse what's available.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from valueflows_node.app.models.sharing_preference import (
    SharingPreference,
    SharingPreferenceCreate,
    SharingPreferenceUpdate,
)
from valueflows_node.app.models.vf.listing import Listing
from valueflows_node.app.repositories.sharing_preference_repo import SharingPreferenceRepository
from valueflows_node.app.repositories.vf.listing_repo import ListingRepository
from valueflows_node.app.services.inter_community_service import InterCommunityService
from valueflows_node.app.api.auth import get_current_user
from app.database.vouch_repository import VouchRepository
from valueflows_node.app.database.db import get_db_path


router = APIRouter(prefix="/discovery", tags=["discovery"])


class DiscoveryResult(BaseModel):
    """A discovered resource with metadata."""
    listing: Listing
    distance_km: Optional[float] = None
    trust_score: Optional[float] = None
    is_cross_community: bool = False


def get_inter_community_service() -> InterCommunityService:
    """Dependency injection for InterCommunityService."""
    db_path = get_db_path()
    sharing_pref_repo = SharingPreferenceRepository(db_path)
    vouch_repo = VouchRepository(db_path)
    return InterCommunityService(sharing_pref_repo, vouch_repo)


def get_listing_repo() -> ListingRepository:
    """Dependency injection for ListingRepository."""
    from valueflows_node.app.database.db import Database
    db = Database()
    return ListingRepository(db.conn)


@router.get("/resources", response_model=List[DiscoveryResult])
async def discover_resources(
    resource_type: Optional[str] = Query(None, description="Filter by resource type (offer/need)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    max_distance_km: Optional[float] = Query(50, description="Maximum distance in kilometers"),
    min_trust: float = Query(0.3, description="Minimum trust score required"),
    current_user = Depends(get_current_user),
    service: InterCommunityService = Depends(get_inter_community_service),
    listing_repo: ListingRepository = Depends(get_listing_repo),
):
    """
    Discover resources from people who've chosen to share widely.

    This is a PULL model - you browse what's available.
    Creators chose to make things visible. You choose what to look at.

    Only returns resources you have permission to see based on:
    1. Creator's visibility settings
    2. Your trust connection to creator
    3. Distance (if applicable)
    4. Block lists
    """
    viewer_id = current_user["id"]

    # Get all listings (offers and needs)
    all_listings = listing_repo.list_listings(
        listing_type=resource_type,
        category=category,
    )

    # Filter to only visible resources
    visible_results = []

    for listing in all_listings:
        # Don't show your own listings in discovery
        if listing.provider_id == viewer_id:
            continue

        # Check if viewer can see this resource
        can_see = await service.can_see_resource(
            viewer_id=viewer_id,
            creator_id=listing.provider_id,
            viewer_community_id=current_user.get("community_id"),
            creator_community_id=getattr(listing, "community_id", None),
            # TODO: Add cell_id, lat/lon from user/listing models
            # viewer_cell_id=current_user.get("cell_id"),
            # creator_cell_id=...,
            # viewer_lat=current_user.get("latitude"),
            # viewer_lon=current_user.get("longitude"),
            # creator_lat=...,
            # creator_lon=...,
        )

        if can_see:
            # Compute metadata for this result
            trust_score = service._compute_trust_between(viewer_id, listing.provider_id)

            is_cross_community = (
                current_user.get("community_id")
                and getattr(listing, "community_id", None)
                and current_user.get("community_id") != getattr(listing, "community_id", None)
            )

            visible_results.append(
                DiscoveryResult(
                    listing=listing,
                    trust_score=trust_score,
                    is_cross_community=is_cross_community,
                )
            )

    # Apply trust filter
    visible_results = [r for r in visible_results if (r.trust_score or 0) >= min_trust]

    # TODO: Apply distance filter when location data is available
    # if max_distance_km:
    #     visible_results = [r for r in visible_results if (r.distance_km or 0) <= max_distance_km]

    return visible_results


@router.get("/preferences/me", response_model=SharingPreference)
async def get_my_sharing_preference(
    current_user = Depends(get_current_user),
    service: InterCommunityService = Depends(get_inter_community_service),
):
    """Get current user's sharing preference."""
    return service.get_sharing_preference(current_user["id"])


@router.put("/preferences/me", response_model=SharingPreference)
async def update_my_sharing_preference(
    update: SharingPreferenceUpdate,
    current_user = Depends(get_current_user),
    service: InterCommunityService = Depends(get_inter_community_service),
):
    """Update current user's sharing preference."""
    # Get current preference
    current_pref = service.get_sharing_preference(current_user["id"])

    # Apply updates
    if update.visibility is not None:
        current_pref.visibility = update.visibility
    if update.location_precision is not None:
        current_pref.location_precision = update.location_precision
    if update.local_radius_km is not None:
        current_pref.local_radius_km = update.local_radius_km

    # Save
    return service.set_sharing_preference(current_pref)


@router.post("/preferences/me", response_model=SharingPreference, status_code=201)
async def create_my_sharing_preference(
    create: SharingPreferenceCreate,
    current_user = Depends(get_current_user),
    service: InterCommunityService = Depends(get_inter_community_service),
):
    """Create sharing preference for current user."""
    preference = SharingPreference(
        user_id=current_user["id"],
        visibility=create.visibility,
        location_precision=create.location_precision,
        local_radius_km=create.local_radius_km,
    )

    return service.set_sharing_preference(preference)
