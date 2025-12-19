"""
Leakage Metrics Repository

Database operations for exchange values and metrics.
Handles privacy-preserving aggregation.
"""

import sqlite3
import json
from typing import Optional, List
from datetime import datetime, timedelta

from ..models.leakage_metrics import (
    ExchangeValue, PersonalMetrics, CommunityMetrics, NetworkMetrics,
    CategoryValueDefault, PeriodType, ValueCategory, EstimationMethod
)


class LeakageMetricsRepository:
    """Repository for leakage metrics data"""

    def __init__(self, db_conn: sqlite3.Connection):
        self.db = db_conn

    # =========================================================================
    # EXCHANGE VALUES
    # =========================================================================

    def create_exchange_value(self, value: ExchangeValue) -> ExchangeValue:
        """Create a new exchange value record"""
        self.db.execute(
            """
            INSERT INTO exchange_values (
                id, exchange_id, category, estimated_value, estimation_method,
                user_override, final_value, included_in_aggregates, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                value.id,
                value.exchange_id,
                value.category.value,
                value.estimated_value,
                value.estimation_method.value,
                value.user_override,
                value.final_value,
                1 if value.included_in_aggregates else 0,
                value.created_at.isoformat() if value.created_at else datetime.now().isoformat(),
            )
        )
        self.db.commit()
        return value

    def find_by_exchange_id(self, exchange_id: str) -> Optional[ExchangeValue]:
        """Find exchange value by exchange ID"""
        cursor = self.db.execute(
            """
            SELECT id, exchange_id, category, estimated_value, estimation_method,
                   user_override, final_value, included_in_aggregates, created_at, updated_at
            FROM exchange_values
            WHERE exchange_id = ?
            """,
            (exchange_id,)
        )
        row = cursor.fetchone()

        if not row:
            return None

        return ExchangeValue(
            id=row[0],
            exchange_id=row[1],
            category=ValueCategory(row[2]),
            estimated_value=row[3],
            estimation_method=EstimationMethod(row[4]),
            user_override=row[5],
            final_value=row[6],
            included_in_aggregates=bool(row[7]),
            created_at=datetime.fromisoformat(row[8]) if row[8] else None,
            updated_at=datetime.fromisoformat(row[9]) if row[9] else None,
        )

    def update_exchange_value(self, value: ExchangeValue) -> ExchangeValue:
        """Update an exchange value (e.g., user override)"""
        value.updated_at = datetime.now()

        self.db.execute(
            """
            UPDATE exchange_values
            SET user_override = ?,
                final_value = ?,
                estimation_method = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                value.user_override,
                value.final_value,
                value.estimation_method.value,
                value.updated_at.isoformat(),
                value.id,
            )
        )
        self.db.commit()
        return value

    # =========================================================================
    # PERSONAL METRICS
    # =========================================================================

    def get_personal_metrics(
        self,
        agent_id: str,
        period_type: PeriodType,
        period_start: datetime
    ) -> Optional[PersonalMetrics]:
        """Get personal metrics for an agent and period"""
        cursor = self.db.execute(
            """
            SELECT id, agent_id, period_type, period_start, period_end,
                   total_value, given_value, received_value, transaction_count,
                   by_category, show_stats, created_at, updated_at
            FROM personal_metrics
            WHERE agent_id = ? AND period_type = ? AND period_start = ?
            """,
            (agent_id, period_type.value, period_start.isoformat())
        )
        row = cursor.fetchone()

        if not row:
            return None

        return PersonalMetrics(
            id=row[0],
            agent_id=row[1],
            period_type=PeriodType(row[2]),
            period_start=datetime.fromisoformat(row[3]),
            period_end=datetime.fromisoformat(row[4]),
            total_value=row[5],
            given_value=row[6],
            received_value=row[7],
            transaction_count=row[8],
            by_category=json.loads(row[9]) if row[9] else {},
            show_stats=bool(row[10]),
            created_at=datetime.fromisoformat(row[11]) if row[11] else None,
            updated_at=datetime.fromisoformat(row[12]) if row[12] else None,
        )

    def upsert_personal_metrics(self, metrics: PersonalMetrics) -> PersonalMetrics:
        """Create or update personal metrics"""
        metrics.updated_at = datetime.now()

        self.db.execute(
            """
            INSERT INTO personal_metrics (
                id, agent_id, period_type, period_start, period_end,
                total_value, given_value, received_value, transaction_count,
                by_category, show_stats, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(agent_id, period_type, period_start) DO UPDATE SET
                total_value = excluded.total_value,
                given_value = excluded.given_value,
                received_value = excluded.received_value,
                transaction_count = excluded.transaction_count,
                by_category = excluded.by_category,
                updated_at = excluded.updated_at
            """,
            (
                metrics.id,
                metrics.agent_id,
                metrics.period_type.value,
                metrics.period_start.isoformat(),
                metrics.period_end.isoformat(),
                metrics.total_value,
                metrics.given_value,
                metrics.received_value,
                metrics.transaction_count,
                json.dumps(metrics.by_category),
                1 if metrics.show_stats else 0,
                metrics.created_at.isoformat() if metrics.created_at else datetime.now().isoformat(),
                metrics.updated_at.isoformat(),
            )
        )
        self.db.commit()
        return metrics

    # =========================================================================
    # COMMUNITY METRICS
    # =========================================================================

    def get_community_metrics(
        self,
        community_id: str,
        period_type: PeriodType,
        period_start: datetime
    ) -> Optional[CommunityMetrics]:
        """Get community metrics for a period"""
        cursor = self.db.execute(
            """
            SELECT id, community_id, period_type, period_start, period_end,
                   total_value, transaction_count, member_count,
                   by_category, created_at, updated_at
            FROM community_metrics
            WHERE community_id = ? AND period_type = ? AND period_start = ?
            """,
            (community_id, period_type.value, period_start.isoformat())
        )
        row = cursor.fetchone()

        if not row:
            return None

        return CommunityMetrics(
            id=row[0],
            community_id=row[1],
            period_type=PeriodType(row[2]),
            period_start=datetime.fromisoformat(row[3]),
            period_end=datetime.fromisoformat(row[4]),
            total_value=row[5],
            transaction_count=row[6],
            member_count=row[7],
            by_category=json.loads(row[8]) if row[8] else {},
            created_at=datetime.fromisoformat(row[9]) if row[9] else None,
            updated_at=datetime.fromisoformat(row[10]) if row[10] else None,
        )

    def upsert_community_metrics(self, metrics: CommunityMetrics) -> CommunityMetrics:
        """Create or update community metrics"""
        metrics.updated_at = datetime.now()

        self.db.execute(
            """
            INSERT INTO community_metrics (
                id, community_id, period_type, period_start, period_end,
                total_value, transaction_count, member_count,
                by_category, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(community_id, period_type, period_start) DO UPDATE SET
                total_value = excluded.total_value,
                transaction_count = excluded.transaction_count,
                member_count = excluded.member_count,
                by_category = excluded.by_category,
                updated_at = excluded.updated_at
            """,
            (
                metrics.id,
                metrics.community_id,
                metrics.period_type.value,
                metrics.period_start.isoformat(),
                metrics.period_end.isoformat(),
                metrics.total_value,
                metrics.transaction_count,
                metrics.member_count,
                json.dumps(metrics.by_category),
                metrics.created_at.isoformat() if metrics.created_at else datetime.now().isoformat(),
                metrics.updated_at.isoformat(),
            )
        )
        self.db.commit()
        return metrics

    # =========================================================================
    # NETWORK METRICS
    # =========================================================================

    def get_network_metrics(
        self,
        period_type: PeriodType,
        period_start: datetime
    ) -> Optional[NetworkMetrics]:
        """Get network-wide metrics for a period"""
        cursor = self.db.execute(
            """
            SELECT id, period_type, period_start, period_end,
                   total_value, transaction_count, active_communities, active_members,
                   by_category, created_at, updated_at
            FROM network_metrics
            WHERE period_type = ? AND period_start = ?
            """,
            (period_type.value, period_start.isoformat())
        )
        row = cursor.fetchone()

        if not row:
            return None

        return NetworkMetrics(
            id=row[0],
            period_type=PeriodType(row[1]),
            period_start=datetime.fromisoformat(row[2]),
            period_end=datetime.fromisoformat(row[3]),
            total_value=row[4],
            transaction_count=row[5],
            active_communities=row[6],
            active_members=row[7],
            by_category=json.loads(row[8]) if row[8] else {},
            created_at=datetime.fromisoformat(row[9]) if row[9] else None,
            updated_at=datetime.fromisoformat(row[10]) if row[10] else None,
        )

    def upsert_network_metrics(self, metrics: NetworkMetrics) -> NetworkMetrics:
        """Create or update network metrics"""
        metrics.updated_at = datetime.now()

        self.db.execute(
            """
            INSERT INTO network_metrics (
                id, period_type, period_start, period_end,
                total_value, transaction_count, active_communities, active_members,
                by_category, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(period_type, period_start) DO UPDATE SET
                total_value = excluded.total_value,
                transaction_count = excluded.transaction_count,
                active_communities = excluded.active_communities,
                active_members = excluded.active_members,
                by_category = excluded.by_category,
                updated_at = excluded.updated_at
            """,
            (
                metrics.id,
                metrics.period_type.value,
                metrics.period_start.isoformat(),
                metrics.period_end.isoformat(),
                metrics.total_value,
                metrics.transaction_count,
                metrics.active_communities,
                metrics.active_members,
                json.dumps(metrics.by_category),
                metrics.created_at.isoformat() if metrics.created_at else datetime.now().isoformat(),
                metrics.updated_at.isoformat(),
            )
        )
        self.db.commit()
        return metrics
