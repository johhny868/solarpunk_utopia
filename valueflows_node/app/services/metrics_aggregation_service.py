"""
Metrics Aggregation Service

Periodically aggregates exchange values into personal, community, and network metrics.
Privacy-preserving: only aggregates are visible, never individual values.
"""

import sqlite3
import uuid
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict

from ..models.leakage_metrics import (
    PersonalMetrics, CommunityMetrics, NetworkMetrics,
    PeriodType, ValueCategory
)
from ..repositories.leakage_metrics_repo import LeakageMetricsRepository


class MetricsAggregationService:
    """Service for aggregating metrics"""

    def __init__(self, db_conn: sqlite3.Connection):
        self.db = db_conn
        self.repo = LeakageMetricsRepository(db_conn)

    def aggregate_all_metrics(self, period_type: PeriodType, period_start: datetime):
        """
        Aggregate all metrics for a given period.
        This should be run periodically (e.g., daily cron job).
        """
        period_end = self._get_period_end(period_type, period_start)

        # 1. Aggregate personal metrics for all users
        self._aggregate_personal_metrics(period_type, period_start, period_end)

        # 2. Aggregate community metrics for all communities
        self._aggregate_community_metrics(period_type, period_start, period_end)

        # 3. Aggregate network-wide metrics
        self._aggregate_network_metrics(period_type, period_start, period_end)

    # =========================================================================
    # PERSONAL METRICS
    # =========================================================================

    def _aggregate_personal_metrics(
        self,
        period_type: PeriodType,
        period_start: datetime,
        period_end: datetime
    ):
        """Aggregate personal metrics for all users in the period"""

        # Get all exchanges in the period with values
        cursor = self.db.execute(
            """
            SELECT
                e.provider_id,
                e.receiver_id,
                ev.category,
                ev.final_value,
                ev.included_in_aggregates
            FROM exchanges e
            JOIN exchange_values ev ON ev.exchange_id = e.id
            WHERE e.status = 'completed'
              AND e.updated_at >= ?
              AND e.updated_at < ?
              AND ev.included_in_aggregates = 1
            """,
            (period_start.isoformat(), period_end.isoformat())
        )

        # Aggregate by agent
        agent_stats = defaultdict(lambda: {
            "given": 0.0,
            "received": 0.0,
            "total": 0.0,
            "count": 0,
            "by_category": defaultdict(float)
        })

        for row in cursor.fetchall():
            provider_id, receiver_id, category, value, _ = row

            # Provider gave
            agent_stats[provider_id]["given"] += value
            agent_stats[provider_id]["total"] += value
            agent_stats[provider_id]["count"] += 1
            agent_stats[provider_id]["by_category"][category] += value

            # Receiver received
            agent_stats[receiver_id]["received"] += value
            agent_stats[receiver_id]["total"] += value
            agent_stats[receiver_id]["count"] += 1
            agent_stats[receiver_id]["by_category"][category] += value

        # Save personal metrics for each agent
        for agent_id, stats in agent_stats.items():
            metrics = PersonalMetrics(
                id=f"pmetrics:{uuid.uuid4()}",
                agent_id=agent_id,
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                total_value=stats["total"],
                given_value=stats["given"],
                received_value=stats["received"],
                transaction_count=stats["count"],
                by_category=dict(stats["by_category"]),
                show_stats=True,
                created_at=datetime.now()
            )

            self.repo.upsert_personal_metrics(metrics)

    # =========================================================================
    # COMMUNITY METRICS
    # =========================================================================

    def _aggregate_community_metrics(
        self,
        period_type: PeriodType,
        period_start: datetime,
        period_end: datetime
    ):
        """Aggregate community metrics for all communities in the period"""

        # Get all exchanges in the period with values, grouped by community
        cursor = self.db.execute(
            """
            SELECT
                e.community_id,
                ev.category,
                SUM(ev.final_value) as total_value,
                COUNT(*) as transaction_count
            FROM exchanges e
            JOIN exchange_values ev ON ev.exchange_id = e.id
            WHERE e.status = 'completed'
              AND e.updated_at >= ?
              AND e.updated_at < ?
              AND ev.included_in_aggregates = 1
              AND e.community_id IS NOT NULL
            GROUP BY e.community_id, ev.category
            """,
            (period_start.isoformat(), period_end.isoformat())
        )

        # Aggregate by community
        community_stats = defaultdict(lambda: {
            "total": 0.0,
            "count": 0,
            "by_category": defaultdict(float)
        })

        for row in cursor.fetchall():
            community_id, category, value, count = row
            community_stats[community_id]["total"] += value
            community_stats[community_id]["count"] += count
            community_stats[community_id]["by_category"][category] = value

        # Get member counts for each community
        for community_id in community_stats.keys():
            cursor = self.db.execute(
                """
                SELECT COUNT(DISTINCT agent_id)
                FROM (
                    SELECT provider_id as agent_id FROM exchanges
                    WHERE community_id = ?
                      AND status = 'completed'
                      AND updated_at >= ?
                      AND updated_at < ?
                    UNION
                    SELECT receiver_id as agent_id FROM exchanges
                    WHERE community_id = ?
                      AND status = 'completed'
                      AND updated_at >= ?
                      AND updated_at < ?
                )
                """,
                (community_id, period_start.isoformat(), period_end.isoformat(),
                 community_id, period_start.isoformat(), period_end.isoformat())
            )
            member_count = cursor.fetchone()[0]

            # Create community metrics
            stats = community_stats[community_id]
            metrics = CommunityMetrics(
                id=f"cmetrics:{uuid.uuid4()}",
                community_id=community_id,
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                total_value=stats["total"],
                transaction_count=stats["count"],
                member_count=member_count,
                by_category=dict(stats["by_category"]),
                created_at=datetime.now()
            )

            self.repo.upsert_community_metrics(metrics)

    # =========================================================================
    # NETWORK METRICS
    # =========================================================================

    def _aggregate_network_metrics(
        self,
        period_type: PeriodType,
        period_start: datetime,
        period_end: datetime
    ):
        """Aggregate network-wide metrics for the period"""

        # Get totals by category
        cursor = self.db.execute(
            """
            SELECT
                ev.category,
                SUM(ev.final_value) as total_value,
                COUNT(*) as transaction_count
            FROM exchanges e
            JOIN exchange_values ev ON ev.exchange_id = e.id
            WHERE e.status = 'completed'
              AND e.updated_at >= ?
              AND e.updated_at < ?
              AND ev.included_in_aggregates = 1
            GROUP BY ev.category
            """,
            (period_start.isoformat(), period_end.isoformat())
        )

        by_category = {}
        total_value = 0.0
        transaction_count = 0

        for row in cursor.fetchall():
            category, value, count = row
            by_category[category] = value
            total_value += value
            transaction_count += count

        # Count active communities
        cursor = self.db.execute(
            """
            SELECT COUNT(DISTINCT community_id)
            FROM exchanges
            WHERE status = 'completed'
              AND updated_at >= ?
              AND updated_at < ?
              AND community_id IS NOT NULL
            """,
            (period_start.isoformat(), period_end.isoformat())
        )
        active_communities = cursor.fetchone()[0]

        # Count active members
        cursor = self.db.execute(
            """
            SELECT COUNT(DISTINCT agent_id)
            FROM (
                SELECT provider_id as agent_id FROM exchanges
                WHERE status = 'completed'
                  AND updated_at >= ?
                  AND updated_at < ?
                UNION
                SELECT receiver_id as agent_id FROM exchanges
                WHERE status = 'completed'
                  AND updated_at >= ?
                  AND updated_at < ?
            )
            """,
            (period_start.isoformat(), period_end.isoformat(),
             period_start.isoformat(), period_end.isoformat())
        )
        active_members = cursor.fetchone()[0]

        # Create network metrics
        metrics = NetworkMetrics(
            id=f"nmetrics:{uuid.uuid4()}",
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            total_value=total_value,
            transaction_count=transaction_count,
            active_communities=active_communities,
            active_members=active_members,
            by_category=by_category,
            created_at=datetime.now()
        )

        self.repo.upsert_network_metrics(metrics)

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _get_period_end(self, period_type: PeriodType, period_start: datetime) -> datetime:
        """Calculate period end from period start"""
        if period_type == PeriodType.DAY:
            return period_start + timedelta(days=1)
        elif period_type == PeriodType.WEEK:
            return period_start + timedelta(weeks=1)
        elif period_type == PeriodType.MONTH:
            # Approximate month as 30 days (could be more precise)
            return period_start + timedelta(days=30)
        elif period_type == PeriodType.YEAR:
            return period_start + timedelta(days=365)
        else:  # ALL_TIME
            return datetime.now()
