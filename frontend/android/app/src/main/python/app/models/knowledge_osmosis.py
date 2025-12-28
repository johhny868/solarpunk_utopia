"""Models for Knowledge Osmosis

'Knowledge emerges only through invention and re-invention.' - Paulo Freire

Study circles share learning artifacts to the Common Heap.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List


class CircleStatus(Enum):
    """Status of a study circle."""
    FORMING = "forming"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ArtifactType(Enum):
    """Type of learning artifact."""
    ZINE = "zine"
    GUIDE = "guide"
    QUESTIONS = "questions"
    RESOURCES = "resources"
    SYNTHESIS = "synthesis"


class QuestionStatus(Enum):
    """Status of an unanswered question."""
    OPEN = "open"
    ANSWERED = "answered"
    EXPLORING = "exploring"


@dataclass
class StudyCircle:
    """A study circle for collaborative learning."""
    id: str
    name: str
    description: Optional[str]
    topic: str
    facilitator_user_id: Optional[str]
    member_count: int = 0
    status: CircleStatus = CircleStatus.FORMING
    artifact_commitment: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: str = None


@dataclass
class LearningArtifact:
    """An artifact created by a study circle."""
    id: str
    circle_id: str
    created_by_user_id: str
    title: str
    description: Optional[str]
    artifact_type: ArtifactType
    content: str  # Markdown
    topic: str
    tags: List[str]
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    language: str = 'en'
    builds_on_artifact_id: Optional[str] = None
    attribution_text: Optional[str] = None
    view_count: int = 0
    use_count: int = 0
    published_at: datetime = None
    updated_at: Optional[datetime] = None


@dataclass
class UnansweredQuestion:
    """A question left by a study circle for others to explore."""
    id: str
    artifact_id: str
    circle_id: str
    question: str
    context: Optional[str]
    status: QuestionStatus = QuestionStatus.OPEN
    answered_by_circle_id: Optional[str] = None
    answer_artifact_id: Optional[str] = None
    asked_at: datetime = None
    answered_at: Optional[datetime] = None
