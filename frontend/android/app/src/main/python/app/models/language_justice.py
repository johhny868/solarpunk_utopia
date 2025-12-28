"""
Language Justice Models

"So, if you want to really hurt me, talk badly about my language." - Gloria Anzaldúa

Multi-language support from the start, not as an afterthought.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class LanguageStatus(str, Enum):
    """Language support status"""

    IN_PROGRESS = "in_progress"
    COMMUNITY_SUPPORTED = "community_supported"
    OFFICIAL = "official"


class TranslationStatus(str, Enum):
    """Translation approval status"""

    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    NEEDS_REVIEW = "needs_review"


class TranslationMethod(str, Enum):
    """How the translation was created"""

    COMMUNITY = "community"
    MACHINE = "machine"
    PROFESSIONAL = "professional"


class IssueType(str, Enum):
    """Translation quality issue types"""

    INCORRECT = "incorrect"
    OFFENSIVE = "offensive"
    CULTURALLY_INSENSITIVE = "culturally_insensitive"
    GRAMMATICALLY_WRONG = "grammatically_wrong"


@dataclass
class SupportedLanguage:
    """A supported language in the system"""

    id: str
    language_code: str  # ISO 639-1
    language_name: str  # 'English', 'Español'
    native_name: str  # Name in that language
    rtl: bool  # Right-to-left script
    status: LanguageStatus
    completion_percentage: float
    lead_translator_id: Optional[str]
    contributor_count: int
    added_at: datetime
    last_updated_at: Optional[datetime]


@dataclass
class TranslationString:
    """A string that needs translation"""

    id: str
    string_key: str  # 'offer.create.title'
    context: Optional[str]
    source_text: str
    source_language: str
    category: Optional[str]  # 'ui', 'errors', 'help'
    component: Optional[str]
    character_limit: Optional[int]
    variables: Optional[List[str]]  # Variable names
    plural_forms: bool
    created_at: datetime
    last_modified_at: Optional[datetime]


@dataclass
class Translation:
    """A translation of a string"""

    id: str
    string_id: str
    language_code: str
    translated_text: str
    translation_status: TranslationStatus
    translation_method: TranslationMethod
    translator_id: Optional[str]
    reviewer_id: Optional[str]
    reviewed_at: Optional[datetime]
    upvotes: int
    downvotes: int
    report_count: int
    adaptation_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@dataclass
class TranslationSuggestion:
    """Community-suggested translation"""

    id: str
    string_id: str
    language_code: str
    suggested_text: str
    suggestion_notes: Optional[str]
    suggested_by: str
    suggested_at: datetime
    status: str  # 'pending', 'accepted', 'rejected'
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]


@dataclass
class LanguageUsageStats:
    """Statistics on language usage"""

    id: str
    period_start: datetime
    period_end: datetime
    total_active_users: int
    users_by_language: Dict[str, int]  # {"en": 150, "es": 80}
    non_english_percentage: float  # Success metric: >20%
    total_translation_strings: int
    fully_translated_languages: int
    community_contributions: int
    calculated_at: datetime


@dataclass
class TranslationContributor:
    """Community translator profile"""

    id: str
    user_id: str
    languages: List[str]  # Language codes they contribute to
    translations_submitted: int
    translations_approved: int
    suggestions_accepted: int
    average_rating: float
    is_verified_translator: bool
    can_review: bool
    first_contribution_at: datetime
    last_contribution_at: Optional[datetime]
