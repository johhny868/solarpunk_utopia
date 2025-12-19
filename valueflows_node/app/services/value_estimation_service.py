"""
Value Estimation Service

Estimates counterfactual economic value of gift economy exchanges.
Uses category defaults, market lookups (when available), and user input.
"""

import sqlite3
from typing import Optional, Dict, Tuple
from datetime import datetime
import uuid

from ..models.leakage_metrics import (
    ExchangeValue, ValueCategory, EstimationMethod,
    CategoryValueDefault
)
from ..models.vf.exchange import Exchange
from ..repositories.vf.resource_spec_repo import ResourceSpecRepository


class ValueEstimationService:
    """Estimates economic value of exchanges"""

    def __init__(self, db_conn: sqlite3.Connection):
        self.db = db_conn

    def estimate_exchange_value(
        self,
        exchange: Exchange,
        user_input_value: Optional[float] = None
    ) -> ExchangeValue:
        """
        Estimate the economic value of an exchange.

        Priority order:
        1. User input (if provided)
        2. Market lookup (if available)
        3. Category default

        Returns ExchangeValue object ready to be saved.
        """
        # Determine category from resource spec
        category = self._determine_category(exchange.resource_spec_id)

        # Get estimated value and method
        if user_input_value is not None:
            estimated_value = user_input_value
            method = EstimationMethod.USER_INPUT
        else:
            estimated_value, method = self._get_estimated_value(
                category,
                exchange.resource_spec_id,
                exchange.quantity,
                exchange.unit
            )

        # Create ExchangeValue
        exchange_value = ExchangeValue(
            id=f"exvalue:{uuid.uuid4()}",
            exchange_id=exchange.id,
            category=category,
            estimated_value=estimated_value,
            estimation_method=method,
            final_value=estimated_value,  # Will be user_override if they correct it
            user_override=None,
            included_in_aggregates=True,
            created_at=datetime.now()
        )

        return exchange_value

    def update_value_override(
        self,
        exchange_value: ExchangeValue,
        new_value: float
    ) -> ExchangeValue:
        """
        User corrects the estimated value.
        Updates to use manual override.
        """
        exchange_value.user_override = new_value
        exchange_value.final_value = new_value
        exchange_value.estimation_method = EstimationMethod.MANUAL_OVERRIDE
        exchange_value.updated_at = datetime.now()

        return exchange_value

    def _determine_category(self, resource_spec_id: str) -> ValueCategory:
        """
        Determine the value category from resource spec.
        Maps resource spec category to ValueCategory enum.
        """
        # Fetch resource spec
        cursor = self.db.execute(
            "SELECT category FROM resource_specs WHERE id = ?",
            (resource_spec_id,)
        )
        row = cursor.fetchone()

        if not row:
            return ValueCategory.OTHER

        spec_category = row[0]

        # Map to ValueCategory
        category_map = {
            "food": ValueCategory.FOOD,
            "tools": ValueCategory.TOOLS,
            "transportation": ValueCategory.TRANSPORT,
            "skills": ValueCategory.SKILLS,
            "labor": ValueCategory.SKILLS,
            "housing": ValueCategory.HOUSING,
            "materials": ValueCategory.GOODS,
            "seeds": ValueCategory.GOODS,
            "knowledge": ValueCategory.SKILLS,
            "other": ValueCategory.OTHER,
        }

        return category_map.get(spec_category, ValueCategory.OTHER)

    def _get_estimated_value(
        self,
        category: ValueCategory,
        resource_spec_id: str,
        quantity: float,
        unit: str
    ) -> Tuple[float, EstimationMethod]:
        """
        Get estimated value using available data.

        Priority:
        1. Market lookup (not implemented yet - would use external API)
        2. Category default

        Returns (value, method)
        """
        # TODO: Market lookup integration (future enhancement)
        # For now, use category defaults

        default_value = self._get_category_default(category, unit)

        if default_value is not None:
            total_value = default_value * quantity
            return (total_value, EstimationMethod.CATEGORY_AVERAGE)
        else:
            # Fallback: conservative estimate
            fallback_values = {
                ValueCategory.FOOD: 10.0,
                ValueCategory.TOOLS: 20.0,
                ValueCategory.TRANSPORT: 15.0,
                ValueCategory.SKILLS: 25.0,
                ValueCategory.HOUSING: 50.0,
                ValueCategory.GOODS: 15.0,
                ValueCategory.OTHER: 10.0,
            }
            return (fallback_values[category] * quantity, EstimationMethod.CATEGORY_AVERAGE)

    def _get_category_default(
        self,
        category: ValueCategory,
        unit: str
    ) -> Optional[float]:
        """
        Get default value for a category.
        Looks up category_value_defaults table.
        """
        # Try exact match first (category + unit)
        cursor = self.db.execute(
            """
            SELECT default_value
            FROM category_value_defaults
            WHERE category = ? AND (unit = ? OR unit = 'item')
            ORDER BY CASE WHEN unit = ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (category.value, unit, unit)
        )
        row = cursor.fetchone()

        if row:
            return row[0]

        # Fallback: any default for this category
        cursor = self.db.execute(
            """
            SELECT default_value
            FROM category_value_defaults
            WHERE category = ?
            LIMIT 1
            """,
            (category.value,)
        )
        row = cursor.fetchone()

        return row[0] if row else None

    def get_category_defaults(self) -> list[CategoryValueDefault]:
        """Get all category defaults for UI display"""
        cursor = self.db.execute(
            """
            SELECT id, category, subcategory, default_value, unit,
                   description, source, created_at, updated_at
            FROM category_value_defaults
            ORDER BY category, subcategory
            """
        )

        defaults = []
        for row in cursor.fetchall():
            defaults.append(CategoryValueDefault(
                id=row[0],
                category=ValueCategory(row[1]),
                subcategory=row[2],
                default_value=row[3],
                unit=row[4],
                description=row[5],
                source=row[6],
                created_at=datetime.fromisoformat(row[7]) if row[7] else None,
                updated_at=datetime.fromisoformat(row[8]) if row[8] else None,
            ))

        return defaults
