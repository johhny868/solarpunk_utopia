"""
Sharing Preference Model

Individual control over resource visibility across communities.
Based on inter-community-sharing proposal.
"""

from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class VisibilityLevel(str):
    """Visibility level constants"""
    MY_CELL = "my_cell"  # Only my immediate cell (5-50 people)
    MY_COMMUNITY = "my_community"  # My whole community
    TRUSTED_NETWORK = "trusted_network"  # Anyone I trust >= 0.5
    ANYONE_LOCAL = "anyone_local"  # Anyone within X km
    NETWORK_WIDE = "network_wide"  # The whole mesh (trust >= 0.1)


class LocationPrecision(str):
    """Location fuzzing for privacy"""
    EXACT = "exact"
    NEIGHBORHOOD = "neighborhood"
    CITY = "city"
    REGION = "region"


class SharingPreference(BaseModel):
    """
    Individual controls their own visibility.

    No gatekeepers. Individuals decide what to share, not stewards.
    """
    user_id: str

    # Who can see my offers/needs?
    visibility: str = VisibilityLevel.TRUSTED_NETWORK  # Default: anyone connected through trust

    # Optional location fuzzing for privacy
    location_precision: str = LocationPrecision.NEIGHBORHOOD

    # For "anyone_local" visibility
    local_radius_km: float = 25.0

    # Metadata
    updated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class SharingPreferenceCreate(BaseModel):
    """Request to create/update sharing preference"""
    visibility: str = VisibilityLevel.TRUSTED_NETWORK
    location_precision: str = LocationPrecision.NEIGHBORHOOD
    local_radius_km: float = 25.0


class SharingPreferenceUpdate(BaseModel):
    """Request to update sharing preference"""
    visibility: Optional[str] = None
    location_precision: Optional[str] = None
    local_radius_km: Optional[float] = None
