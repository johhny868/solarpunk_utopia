"""
Reflection and Dialogue Models

GAP-59: Conscientization Prompts (Paulo Freire)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FreireanPrinciple(str, Enum):
    """Freirean pedagogical principles"""
    PROBLEM_POSING = "problem-posing"
    CRITICAL_REFLECTION = "critical-reflection"
    PRAXIS = "praxis"
    DIALOGUE = "dialogue"


class PromptTrigger(str, Enum):
    """Events that trigger reflection prompts"""
    FIRST_OFFER = "first_offer"
    FIRST_NEED = "first_need"
    EXCHANGE_COMPLETE = "exchange_complete"
    WEEKLY = "weekly"
    MILESTONE = "milestone"


class Reflection(BaseModel):
    """
    Individual reflection on a conscientization prompt.

    Can be anonymous and optionally shared with community.
    """
    id: str
    user_id: Optional[str] = None  # Anonymous if None
    prompt_id: str
    response: str = Field(..., min_length=1, max_length=5000)
    context: dict = Field(default_factory=dict)  # What triggered the prompt
    created_at: datetime
    anonymous: bool = False
    shared_with_community: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "id": "refl_123",
                "user_id": None,  # Anonymous
                "prompt_id": "first-offer",
                "response": "I wanted to share because I have more apples than I can eat...",
                "context": {"offer_id": "offer_456"},
                "created_at": "2025-12-19T10:00:00Z",
                "anonymous": True,
                "shared_with_community": False
            }
        }


class Voice(BaseModel):
    """A voice in a collective dialogue"""
    id: str
    author_id: Optional[str] = None  # Anonymous if None
    text: str = Field(..., min_length=1, max_length=2000)
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "voice_789",
                "author_id": None,  # Anonymous
                "text": "I notice some people offer a lot more than others. Maybe they have more privilege?",
                "created_at": "2025-12-19T10:05:00Z"
            }
        }


class Dialogue(BaseModel):
    """
    Collective problem-posing dialogue.

    Based on Freire's idea that we educate each other, mediated by the world.
    Surfaces tensions and contradictions, not seeking consensus.
    """
    id: str
    problem: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="The tension/contradiction being explored"
    )
    voices: List[Voice] = Field(default_factory=list)
    synthesis: Optional[str] = Field(
        None,
        max_length=2000,
        description="Emergent understanding (not conclusion)"
    )
    created_at: datetime
    commune_id: str
    auto_generated: bool = False  # Generated from data patterns

    class Config:
        json_schema_extra = {
            "example": {
                "id": "dialogue_101",
                "problem": "Some people offer a lot, others rarely. Why?",
                "voices": [
                    {
                        "id": "voice_1",
                        "author_id": None,
                        "text": "Maybe some have more free time?",
                        "created_at": "2025-12-19T10:00:00Z"
                    },
                    {
                        "id": "voice_2",
                        "author_id": None,
                        "text": "Or more resources to share without worry",
                        "created_at": "2025-12-19T10:05:00Z"
                    }
                ],
                "synthesis": None,  # Emerges from community
                "created_at": "2025-12-19T09:00:00Z",
                "commune_id": "commune_1",
                "auto_generated": True
            }
        }


class DialogueCreate(BaseModel):
    """Request to create a new dialogue"""
    problem: str = Field(..., min_length=10, max_length=500)
    commune_id: str
    initial_voice: Optional[str] = Field(None, max_length=2000)

    class Config:
        json_schema_extra = {
            "example": {
                "problem": "Who's participating, who isn't? What does that tell us?",
                "commune_id": "commune_1",
                "initial_voice": "I've noticed the same people commenting on everything..."
            }
        }


class VoiceCreate(BaseModel):
    """Request to add a voice to a dialogue"""
    dialogue_id: str
    text: str = Field(..., min_length=1, max_length=2000)
    anonymous: bool = True  # Default to anonymous

    class Config:
        json_schema_extra = {
            "example": {
                "dialogue_id": "dialogue_101",
                "text": "What if we're replicating the same power dynamics we're trying to escape?",
                "anonymous": True
            }
        }
