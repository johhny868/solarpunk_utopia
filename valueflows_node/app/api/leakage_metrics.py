"""Leakage Metrics API Endpoints"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import uuid

from ..models.leakage_metrics import PeriodType
from ..database import get_database
from ..repositories.leakage_metrics_repo import LeakageMetricsRepository
from ..services.value_estimation_service import ValueEstimationService
from ..services.metrics_aggregation_service import MetricsAggregationService

router = APIRouter(prefix="/leakage-metrics", tags=["leakage-metrics"])


@router.get("/personal/{agent_id}", response_model=dict)
async def get_personal_metrics(
    agent_id: str,
    period_type: str = "month"
):
    """Get personal impact metrics for an agent"""
    try:
        db = get_database()
        db.connect()
        repo = LeakageMetricsRepository(db.conn)

        # Get current period
        now = datetime.now()
        period_type_enum = PeriodType(period_type)

        if period_type_enum == PeriodType.MONTH:
            period_start = datetime(now.year, now.month, 1)
        elif period_type_enum == PeriodType.WEEK:
            period_start = now - timedelta(days=now.weekday())
        elif period_type_enum == PeriodType.DAY:
            period_start = datetime(now.year, now.month, now.day)
        else:
            period_start = datetime(now.year, 1, 1)

        metrics = repo.get_personal_metrics(agent_id, period_type_enum, period_start)

        db.close()

        if not metrics:
            return {
                "found": False,
                "message": "No metrics for this period yet"
            }

        # Only return if user allows stats to be shown
        if not metrics.show_stats:
            return {
                "found": False,
                "message": "User has disabled stats visibility"
            }

        return {
            "found": True,
            "metrics": metrics.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/community/{community_id}", response_model=dict)
async def get_community_metrics(
    community_id: str,
    period_type: str = "month"
):
    """Get community impact metrics"""
    try:
        db = get_database()
        db.connect()
        repo = LeakageMetricsRepository(db.conn)

        # Get current period
        now = datetime.now()
        period_type_enum = PeriodType(period_type)

        if period_type_enum == PeriodType.MONTH:
            period_start = datetime(now.year, now.month, 1)
        elif period_type_enum == PeriodType.WEEK:
            period_start = now - timedelta(days=now.weekday())
        elif period_type_enum == PeriodType.DAY:
            period_start = datetime(now.year, now.month, now.day)
        else:
            period_start = datetime(now.year, 1, 1)

        metrics = repo.get_community_metrics(community_id, period_type_enum, period_start)

        db.close()

        if not metrics:
            return {
                "found": False,
                "message": "No metrics for this period yet"
            }

        return {
            "found": True,
            "metrics": metrics.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/network", response_model=dict)
async def get_network_metrics(period_type: str = "month"):
    """Get network-wide impact metrics"""
    try:
        db = get_database()
        db.connect()
        repo = LeakageMetricsRepository(db.conn)

        # Get current period
        now = datetime.now()
        period_type_enum = PeriodType(period_type)

        if period_type_enum == PeriodType.MONTH:
            period_start = datetime(now.year, now.month, 1)
        elif period_type_enum == PeriodType.WEEK:
            period_start = now - timedelta(days=now.weekday())
        elif period_type_enum == PeriodType.DAY:
            period_start = datetime(now.year, now.month, now.day)
        else:
            period_start = datetime(now.year, 1, 1)

        metrics = repo.get_network_metrics(period_type_enum, period_start)

        db.close()

        if not metrics:
            return {
                "found": False,
                "message": "No metrics for this period yet"
            }

        return {
            "found": True,
            "metrics": metrics.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/exchange/{exchange_id}/override-value", response_model=dict)
async def override_exchange_value(
    exchange_id: str,
    new_value: float,
    agent_id: str
):
    """
    Allow user to correct the estimated value of an exchange.
    Only the provider or receiver can override.
    """
    try:
        db = get_database()
        db.connect()

        # Verify agent is involved in this exchange
        cursor = db.conn.execute(
            "SELECT provider_id, receiver_id FROM exchanges WHERE id = ?",
            (exchange_id,)
        )
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Exchange not found")

        provider_id, receiver_id = row
        if agent_id not in [provider_id, receiver_id]:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Get and update value
        repo = LeakageMetricsRepository(db.conn)
        value_service = ValueEstimationService(db.conn)

        exchange_value = repo.find_by_exchange_id(exchange_id)
        if not exchange_value:
            raise HTTPException(status_code=404, detail="Exchange value not found")

        updated_value = value_service.update_value_override(exchange_value, new_value)
        repo.update_exchange_value(updated_value)

        db.close()

        return {
            "status": "updated",
            "exchange_value": updated_value.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/aggregate/{period_type}", response_model=dict)
async def trigger_aggregation(period_type: str):
    """
    Manually trigger metrics aggregation for a period.
    Normally this runs on a cron job.
    """
    try:
        db = get_database()
        db.connect()

        aggregation_service = MetricsAggregationService(db.conn)

        # Get current period
        now = datetime.now()
        period_type_enum = PeriodType(period_type)

        if period_type_enum == PeriodType.MONTH:
            period_start = datetime(now.year, now.month, 1)
        elif period_type_enum == PeriodType.WEEK:
            period_start = now - timedelta(days=now.weekday())
        elif period_type_enum == PeriodType.DAY:
            period_start = datetime(now.year, now.month, now.day)
        else:
            period_start = datetime(now.year, 1, 1)

        aggregation_service.aggregate_all_metrics(period_type_enum, period_start)

        db.close()

        return {
            "status": "aggregated",
            "period_type": period_type,
            "period_start": period_start.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/category-defaults", response_model=dict)
async def get_category_defaults():
    """Get all category value defaults"""
    try:
        db = get_database()
        db.connect()

        value_service = ValueEstimationService(db.conn)
        defaults = value_service.get_category_defaults()

        db.close()

        return {
            "defaults": [d.to_dict() for d in defaults]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
