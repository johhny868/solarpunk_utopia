"""
Leakage Metrics Models

Track counterfactual economic value of gift economy transactions.
Privacy-preserving: individual values never public, only aggregates.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict
from enum import Enum


class ValueCategory(str, Enum):
    """Categories for valuing exchanges"""
    FOOD = "food"
    TOOLS = "tools"
    TRANSPORT = "transport"
    SKILLS = "skills"
    HOUSING = "housing"
    GOODS = "goods"
    OTHER = "other"


class EstimationMethod(str, Enum):
    """How the value was estimated"""
    MARKET_LOOKUP = "market_lookup"      # Looked up market price
    USER_INPUT = "user_input"            # User provided estimate
    CATEGORY_AVERAGE = "category_average"  # Used category default
    MANUAL_OVERRIDE = "manual_override"  # User corrected estimate


class PeriodType(str, Enum):
    """Time period granularity"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL_TIME = "all_time"


@dataclass
class ExchangeValue:
    """
    Economic value of a single exchange.
    Individual values are NEVER publicly visible.
    """
    id: str
    exchange_id: str
    category: ValueCategory
    estimated_value: float  # In local currency
    estimation_method: EstimationMethod
    final_value: float  # Either estimated or user override
    user_override: Optional[float] = None
    included_in_aggregates: bool = True  # Privacy control
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "exchange_id": self.exchange_id,
            "category": self.category.value,
            "estimated_value": self.estimated_value,
            "estimation_method": self.estimation_method.value,
            "user_override": self.user_override,
            "final_value": self.final_value,
            "included_in_aggregates": self.included_in_aggregates,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExchangeValue":
        return cls(
            id=data["id"],
            exchange_id=data["exchange_id"],
            category=ValueCategory(data["category"]),
            estimated_value=data["estimated_value"],
            estimation_method=EstimationMethod(data["estimation_method"]),
            user_override=data.get("user_override"),
            final_value=data["final_value"],
            included_in_aggregates=bool(data.get("included_in_aggregates", True)),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


@dataclass
class PersonalMetrics:
    """
    Personal impact metrics for an individual.
    Visible only to the user themselves.
    """
    id: str
    agent_id: str
    period_type: PeriodType
    period_start: datetime
    period_end: datetime
    total_value: float
    given_value: float      # As provider
    received_value: float   # As receiver
    transaction_count: int
    by_category: Dict[str, float]  # Breakdown by category
    show_stats: bool = True  # Privacy control
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "period_type": self.period_type.value,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_value": self.total_value,
            "given_value": self.given_value,
            "received_value": self.received_value,
            "transaction_count": self.transaction_count,
            "by_category": self.by_category,
            "show_stats": self.show_stats,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PersonalMetrics":
        import json
        return cls(
            id=data["id"],
            agent_id=data["agent_id"],
            period_type=PeriodType(data["period_type"]),
            period_start=datetime.fromisoformat(data["period_start"]),
            period_end=datetime.fromisoformat(data["period_end"]),
            total_value=data["total_value"],
            given_value=data["given_value"],
            received_value=data["received_value"],
            transaction_count=data["transaction_count"],
            by_category=json.loads(data["by_category"]) if isinstance(data["by_category"], str) else data["by_category"],
            show_stats=bool(data.get("show_stats", True)),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


@dataclass
class CommunityMetrics:
    """
    Community-level aggregated metrics.
    Visible to community members.
    """
    id: str
    community_id: str
    period_type: PeriodType
    period_start: datetime
    period_end: datetime
    total_value: float
    transaction_count: int
    member_count: int  # Active members in period
    by_category: Dict[str, float]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "community_id": self.community_id,
            "period_type": self.period_type.value,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_value": self.total_value,
            "transaction_count": self.transaction_count,
            "member_count": self.member_count,
            "by_category": self.by_category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CommunityMetrics":
        import json
        return cls(
            id=data["id"],
            community_id=data["community_id"],
            period_type=PeriodType(data["period_type"]),
            period_start=datetime.fromisoformat(data["period_start"]),
            period_end=datetime.fromisoformat(data["period_end"]),
            total_value=data["total_value"],
            transaction_count=data["transaction_count"],
            member_count=data["member_count"],
            by_category=json.loads(data["by_category"]) if isinstance(data["by_category"], str) else data["by_category"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


@dataclass
class NetworkMetrics:
    """
    Network-wide metrics.
    Visible to all users to show collective impact.
    """
    id: str
    period_type: PeriodType
    period_start: datetime
    period_end: datetime
    total_value: float
    transaction_count: int
    active_communities: int
    active_members: int
    by_category: Dict[str, float]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "period_type": self.period_type.value,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_value": self.total_value,
            "transaction_count": self.transaction_count,
            "active_communities": self.active_communities,
            "active_members": self.active_members,
            "by_category": self.by_category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NetworkMetrics":
        import json
        return cls(
            id=data["id"],
            period_type=PeriodType(data["period_type"]),
            period_start=datetime.fromisoformat(data["period_start"]),
            period_end=datetime.fromisoformat(data["period_end"]),
            total_value=data["total_value"],
            transaction_count=data["transaction_count"],
            active_communities=data["active_communities"],
            active_members=data["active_members"],
            by_category=json.loads(data["by_category"]) if isinstance(data["by_category"], str) else data["by_category"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


@dataclass
class CategoryValueDefault:
    """
    Default value estimates for resource categories.
    Used when no specific market price is available.
    """
    id: str
    category: ValueCategory
    subcategory: Optional[str]
    default_value: float
    unit: str
    description: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category.value,
            "subcategory": self.subcategory,
            "default_value": self.default_value,
            "unit": self.unit,
            "description": self.description,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CategoryValueDefault":
        return cls(
            id=data["id"],
            category=ValueCategory(data["category"]),
            subcategory=data.get("subcategory"),
            default_value=data["default_value"],
            unit=data["unit"],
            description=data.get("description"),
            source=data.get("source"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )
