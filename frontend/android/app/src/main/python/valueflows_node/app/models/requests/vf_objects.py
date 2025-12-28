"""
Pydantic Validation Models for ValueFlows Objects

GAP-43: Input Validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

# Import VF enum types
from ..vf.resource_spec import ResourceCategory


class ResourceSpecCreate(BaseModel):
    """
    Request model for creating a resource specification.

    Validates:
    - Required fields present
    - Field types correct
    - String lengths reasonable
    - Category is valid enum value
    """

    name: str = Field(..., min_length=1, max_length=200)
    category: ResourceCategory
    description: Optional[str] = Field(None, max_length=2000)
    subcategory: Optional[str] = Field(None, max_length=100)
    image_url: Optional[str] = Field(None, max_length=500)
    unit: Optional[str] = Field(None, max_length=50, description="Default unit (e.g., 'lbs', 'hours')")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace"""
        if not v or len(v.strip()) == 0:
            raise ValueError("name cannot be empty")
        return v.strip()

    @field_validator('image_url')
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        """Basic URL validation"""
        if v and not v.startswith(('http://', 'https://', 'ipfs://')):
            raise ValueError("image_url must be a valid URL")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tomatoes",
                "category": "food",
                "subcategory": "Vegetables",
                "description": "Fresh garden tomatoes",
                "unit": "lbs"
            }
        }


class AgentCreate(BaseModel):
    """
    Request model for creating a ValueFlows agent.

    Validates:
    - Required fields present
    - Field types correct
    - String lengths reasonable
    """

    name: str = Field(..., min_length=1, max_length=200)
    note: Optional[str] = Field(None, max_length=2000)
    image: Optional[str] = Field(None, max_length=500)
    primary_location: Optional[str] = Field(None, max_length=200)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace"""
        if not v or len(v.strip()) == 0:
            raise ValueError("name cannot be empty")
        return v.strip()

    @field_validator('image')
    @classmethod
    def validate_image_url(cls, v: Optional[str]) -> Optional[str]:
        """Basic URL validation"""
        if v and not v.startswith(('http://', 'https://', 'ipfs://')):
            raise ValueError("image must be a valid URL")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Alice",
                "note": "Community organizer and gardener",
                "primary_location": "Portland, OR"
            }
        }


class CommitmentCreate(BaseModel):
    """
    Request model for creating a commitment.

    Validates:
    - Required fields present
    - Field types correct
    - Numeric ranges valid
    """

    provider: str = Field(..., min_length=1, max_length=200)
    receiver: str = Field(..., min_length=1, max_length=200)
    resource_spec_id: str = Field(..., min_length=1, max_length=200)
    quantity: float = Field(..., gt=0, le=1000000)
    unit: str = Field(default="items", max_length=50)
    due: Optional[datetime] = None
    note: Optional[str] = Field(None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "agent:alice",
                "receiver": "agent:bob",
                "resource_spec_id": "resource_spec:tomatoes",
                "quantity": 5.0,
                "unit": "lbs",
                "due": "2025-12-25T12:00:00",
                "note": "Delivery at community garden"
            }
        }


class CommitmentUpdate(BaseModel):
    """
    Request model for updating a commitment.

    All fields optional - only provided fields are updated.
    """

    quantity: Optional[float] = Field(None, gt=0, le=1000000)
    unit: Optional[str] = Field(None, max_length=50)
    due: Optional[datetime] = None
    note: Optional[str] = Field(None, max_length=2000)
    finished: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "finished": True,
                "note": "Delivered successfully!"
            }
        }


class MatchCreate(BaseModel):
    """
    Request model for creating a match between offer and need.

    Validates:
    - Required fields present
    - Field types correct
    """

    offer_listing_id: str = Field(..., min_length=1, max_length=200)
    need_listing_id: str = Field(..., min_length=1, max_length=200)
    matched_quantity: float = Field(..., gt=0, le=1000000)
    unit: str = Field(default="items", max_length=50)
    match_score: Optional[float] = Field(None, ge=0, le=1)
    explanation: Optional[str] = Field(None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "offer_listing_id": "listing:offer_123",
                "need_listing_id": "listing:need_456",
                "matched_quantity": 3.0,
                "unit": "lbs",
                "match_score": 0.95,
                "explanation": "Both near community garden, quantities align"
            }
        }


class ExchangeCreate(BaseModel):
    """
    Request model for creating an exchange.

    Validates:
    - Required fields present
    - Field types correct
    """

    name: str = Field(..., min_length=1, max_length=200)
    note: Optional[str] = Field(None, max_length=2000)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Ensure name is not just whitespace"""
        if not v or len(v.strip()) == 0:
            raise ValueError("name cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tomatoes for Childcare",
                "note": "Exchange coordinated by mutual aid matchmaker"
            }
        }
