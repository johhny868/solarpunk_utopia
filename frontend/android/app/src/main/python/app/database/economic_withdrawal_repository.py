"""Repository for Economic Withdrawal data access

Every transaction in the gift economy is a transaction that DIDN'T go to Bezos.

Coordinated campaigns to redirect spending from extractive corporations to
regenerative community systems.
"""
import sqlite3
import json
from typing import List, Optional
from datetime import datetime
import uuid

from app.models.economic_withdrawal import (
    Campaign,
    CampaignPledge,
    CorporateAlternative,
    ExitProgress,
    BulkBuyOrder,
    BulkBuyCommitment,
    CampaignType,
    CampaignStatus,
    PledgeStatus,
)


class EconomicWithdrawalRepository:
    """Database access for economic withdrawal campaigns."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ===== Campaigns =====

    def create_campaign(self, campaign: Campaign) -> Campaign:
        """Create a new economic withdrawal campaign."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO campaigns (
                id, campaign_type, name, description,
                target_corporation, target_category,
                cell_id, network_wide,
                created_by, threshold_participants, current_participants,
                status,
                pledge_deadline, campaign_start, campaign_end,
                estimated_economic_impact, network_value_circulated, local_transactions_facilitated,
                created_at, updated_at, activated_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign.id,
            campaign.campaign_type.value,
            campaign.name,
            campaign.description,
            campaign.target_corporation,
            campaign.target_category,
            campaign.cell_id,
            1 if campaign.network_wide else 0,
            campaign.created_by,
            campaign.threshold_participants,
            campaign.current_participants,
            campaign.status.value,
            campaign.pledge_deadline.isoformat(),
            campaign.campaign_start.isoformat(),
            campaign.campaign_end.isoformat(),
            campaign.estimated_economic_impact,
            campaign.network_value_circulated,
            campaign.local_transactions_facilitated,
            campaign.created_at.isoformat(),
            campaign.updated_at.isoformat(),
            campaign.activated_at.isoformat() if campaign.activated_at else None,
            campaign.completed_at.isoformat() if campaign.completed_at else None,
        ))

        conn.commit()
        conn.close()
        return campaign

    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """Get a campaign by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_campaign(row)

    def update_campaign(self, campaign: Campaign) -> Campaign:
        """Update an existing campaign."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE campaigns SET
                current_participants = ?,
                status = ?,
                estimated_economic_impact = ?,
                network_value_circulated = ?,
                local_transactions_facilitated = ?,
                updated_at = ?,
                activated_at = ?,
                completed_at = ?
            WHERE id = ?
        """, (
            campaign.current_participants,
            campaign.status.value,
            campaign.estimated_economic_impact,
            campaign.network_value_circulated,
            campaign.local_transactions_facilitated,
            campaign.updated_at.isoformat(),
            campaign.activated_at.isoformat() if campaign.activated_at else None,
            campaign.completed_at.isoformat() if campaign.completed_at else None,
            campaign.id,
        ))

        conn.commit()
        conn.close()
        return campaign

    def get_campaigns_by_cell(self, cell_id: str) -> List[Campaign]:
        """Get all campaigns for a cell."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM campaigns WHERE cell_id = ? ORDER BY created_at DESC", (cell_id,))
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_campaign(row) for row in rows]

    def get_network_wide_campaigns(self) -> List[Campaign]:
        """Get all network-wide campaigns."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM campaigns WHERE network_wide = 1 ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_campaign(row) for row in rows]

    def get_active_campaigns(self, cell_id: Optional[str] = None) -> List[Campaign]:
        """Get active campaigns (GATHERING or ACTIVE status)."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if cell_id:
            cursor.execute("""
                SELECT * FROM campaigns
                WHERE (cell_id = ? OR network_wide = 1)
                  AND status IN ('gathering', 'active')
                ORDER BY created_at DESC
            """, (cell_id,))
        else:
            cursor.execute("""
                SELECT * FROM campaigns
                WHERE status IN ('gathering', 'active')
                ORDER BY created_at DESC
            """)

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_campaign(row) for row in rows]

    def _row_to_campaign(self, row: sqlite3.Row) -> Campaign:
        """Convert database row to Campaign model."""
        return Campaign(
            id=row['id'],
            campaign_type=CampaignType(row['campaign_type']),
            name=row['name'],
            description=row['description'],
            target_corporation=row['target_corporation'],
            target_category=row['target_category'],
            cell_id=row['cell_id'],
            network_wide=bool(row['network_wide']),
            created_by=row['created_by'],
            threshold_participants=row['threshold_participants'],
            current_participants=row['current_participants'],
            status=CampaignStatus(row['status']),
            pledge_deadline=datetime.fromisoformat(row['pledge_deadline']),
            campaign_start=datetime.fromisoformat(row['campaign_start']),
            campaign_end=datetime.fromisoformat(row['campaign_end']),
            estimated_economic_impact=row['estimated_economic_impact'],
            network_value_circulated=row['network_value_circulated'],
            local_transactions_facilitated=row['local_transactions_facilitated'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            activated_at=datetime.fromisoformat(row['activated_at']) if row['activated_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
        )

    # ===== Pledges =====

    def create_pledge(self, pledge: CampaignPledge) -> CampaignPledge:
        """Create a new campaign pledge."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO campaign_pledges (
                id, campaign_id, user_id,
                commitment_level, commitment_notes,
                status,
                times_avoided_target, estimated_spending_redirected, alternatives_used,
                buddy_id,
                pledged_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pledge.id,
            pledge.campaign_id,
            pledge.user_id,
            pledge.commitment_level,
            pledge.commitment_notes,
            pledge.status.value,
            pledge.times_avoided_target,
            pledge.estimated_spending_redirected,
            pledge.alternatives_used,
            pledge.buddy_id,
            pledge.pledged_at.isoformat(),
            pledge.updated_at.isoformat(),
        ))

        conn.commit()
        conn.close()
        return pledge

    def get_pledge(self, pledge_id: str) -> Optional[CampaignPledge]:
        """Get a pledge by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM campaign_pledges WHERE id = ?", (pledge_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_pledge(row)

    def get_user_pledge_for_campaign(self, user_id: str, campaign_id: str) -> Optional[CampaignPledge]:
        """Get a user's pledge for a specific campaign."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM campaign_pledges WHERE user_id = ? AND campaign_id = ?",
            (user_id, campaign_id)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_pledge(row)

    def update_pledge(self, pledge: CampaignPledge) -> CampaignPledge:
        """Update an existing pledge."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE campaign_pledges SET
                status = ?,
                times_avoided_target = ?,
                estimated_spending_redirected = ?,
                alternatives_used = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            pledge.status.value,
            pledge.times_avoided_target,
            pledge.estimated_spending_redirected,
            pledge.alternatives_used,
            pledge.updated_at.isoformat(),
            pledge.id,
        ))

        conn.commit()
        conn.close()
        return pledge

    def get_campaign_pledges(self, campaign_id: str) -> List[CampaignPledge]:
        """Get all pledges for a campaign."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM campaign_pledges WHERE campaign_id = ? ORDER BY pledged_at DESC",
            (campaign_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_pledge(row) for row in rows]

    def get_user_pledges(self, user_id: str) -> List[CampaignPledge]:
        """Get all pledges by a user."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM campaign_pledges WHERE user_id = ? ORDER BY pledged_at DESC",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_pledge(row) for row in rows]

    def _row_to_pledge(self, row: sqlite3.Row) -> CampaignPledge:
        """Convert database row to CampaignPledge model."""
        return CampaignPledge(
            id=row['id'],
            campaign_id=row['campaign_id'],
            user_id=row['user_id'],
            commitment_level=row['commitment_level'],
            commitment_notes=row['commitment_notes'],
            status=PledgeStatus(row['status']),
            times_avoided_target=row['times_avoided_target'],
            estimated_spending_redirected=row['estimated_spending_redirected'],
            alternatives_used=row['alternatives_used'],
            buddy_id=row['buddy_id'],
            pledged_at=datetime.fromisoformat(row['pledged_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
        )

    # ===== Corporate Alternatives =====

    def create_alternative(self, alternative: CorporateAlternative) -> CorporateAlternative:
        """Create a corporate alternative."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO corporate_alternatives (
                id, campaign_type,
                replaces_corporation, replaces_service,
                alternative_type, name, description,
                cell_id, network_wide,
                contact_user_id, access_instructions,
                times_used,
                created_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alternative.id,
            alternative.campaign_type.value,
            alternative.replaces_corporation,
            alternative.replaces_service,
            alternative.alternative_type,
            alternative.name,
            alternative.description,
            alternative.cell_id,
            1 if alternative.network_wide else 0,
            alternative.contact_user_id,
            alternative.access_instructions,
            alternative.times_used,
            alternative.created_at.isoformat(),
            alternative.created_by,
        ))

        conn.commit()
        conn.close()
        return alternative

    def get_alternatives_for_campaign_type(
        self,
        campaign_type: CampaignType,
        cell_id: Optional[str] = None
    ) -> List[CorporateAlternative]:
        """Get alternatives for a campaign type."""
        conn = self._get_connection()
        cursor = conn.cursor()

        if cell_id:
            cursor.execute("""
                SELECT * FROM corporate_alternatives
                WHERE campaign_type = ?
                  AND (cell_id = ? OR network_wide = 1)
                ORDER BY times_used DESC
            """, (campaign_type.value, cell_id))
        else:
            cursor.execute("""
                SELECT * FROM corporate_alternatives
                WHERE campaign_type = ?
                ORDER BY times_used DESC
            """, (campaign_type.value,))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_alternative(row) for row in rows]

    def increment_alternative_usage(self, alternative_id: str):
        """Increment the usage count for an alternative."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE corporate_alternatives
            SET times_used = times_used + 1
            WHERE id = ?
        """, (alternative_id,))

        conn.commit()
        conn.close()

    def _row_to_alternative(self, row: sqlite3.Row) -> CorporateAlternative:
        """Convert database row to CorporateAlternative model."""
        return CorporateAlternative(
            id=row['id'],
            campaign_type=CampaignType(row['campaign_type']),
            replaces_corporation=row['replaces_corporation'],
            replaces_service=row['replaces_service'],
            alternative_type=row['alternative_type'],
            name=row['name'],
            description=row['description'],
            cell_id=row['cell_id'],
            network_wide=bool(row['network_wide']),
            contact_user_id=row['contact_user_id'],
            access_instructions=row['access_instructions'],
            times_used=row['times_used'],
            created_at=datetime.fromisoformat(row['created_at']),
            created_by=row['created_by'],
        )

    # ===== Exit Progress =====

    def create_exit_progress(self, progress: ExitProgress) -> ExitProgress:
        """Create exit progress record."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO exit_progress (
                id, user_id,
                categories,
                total_estimated_redirected, campaigns_participated, campaigns_completed,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            progress.id,
            progress.user_id,
            json.dumps(progress.categories),
            progress.total_estimated_redirected,
            progress.campaigns_participated,
            progress.campaigns_completed,
            progress.created_at.isoformat(),
            progress.updated_at.isoformat(),
        ))

        conn.commit()
        conn.close()
        return progress

    def get_exit_progress(self, user_id: str) -> Optional[ExitProgress]:
        """Get exit progress for a user."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM exit_progress WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_exit_progress(row)

    def update_exit_progress(self, progress: ExitProgress) -> ExitProgress:
        """Update exit progress."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE exit_progress SET
                categories = ?,
                total_estimated_redirected = ?,
                campaigns_participated = ?,
                campaigns_completed = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            json.dumps(progress.categories),
            progress.total_estimated_redirected,
            progress.campaigns_participated,
            progress.campaigns_completed,
            progress.updated_at.isoformat(),
            progress.id,
        ))

        conn.commit()
        conn.close()
        return progress

    def _row_to_exit_progress(self, row: sqlite3.Row) -> ExitProgress:
        """Convert database row to ExitProgress model."""
        return ExitProgress(
            id=row['id'],
            user_id=row['user_id'],
            categories=json.loads(row['categories']),
            total_estimated_redirected=row['total_estimated_redirected'],
            campaigns_participated=row['campaigns_participated'],
            campaigns_completed=row['campaigns_completed'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
        )

    # ===== Bulk Buys =====

    def create_bulk_buy(self, bulk_buy: BulkBuyOrder) -> BulkBuyOrder:
        """Create a bulk buy order."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bulk_buy_orders (
                id, campaign_id,
                item_name, item_description, unit,
                retail_price_per_unit, wholesale_price_per_unit, savings_percent,
                minimum_units, current_committed_units,
                cell_id, coordinator_id, supplier,
                commitment_deadline, delivery_date, distribution_location,
                status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            bulk_buy.id,
            bulk_buy.campaign_id,
            bulk_buy.item_name,
            bulk_buy.item_description,
            bulk_buy.unit,
            bulk_buy.retail_price_per_unit,
            bulk_buy.wholesale_price_per_unit,
            bulk_buy.savings_percent,
            bulk_buy.minimum_units,
            bulk_buy.current_committed_units,
            bulk_buy.cell_id,
            bulk_buy.coordinator_id,
            bulk_buy.supplier,
            bulk_buy.commitment_deadline.isoformat(),
            bulk_buy.delivery_date.isoformat(),
            bulk_buy.distribution_location,
            bulk_buy.status,
            bulk_buy.created_at.isoformat(),
            bulk_buy.updated_at.isoformat(),
        ))

        conn.commit()
        conn.close()
        return bulk_buy

    def get_bulk_buy(self, bulk_buy_id: str) -> Optional[BulkBuyOrder]:
        """Get a bulk buy order."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bulk_buy_orders WHERE id = ?", (bulk_buy_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return self._row_to_bulk_buy(row)

    def update_bulk_buy(self, bulk_buy: BulkBuyOrder) -> BulkBuyOrder:
        """Update a bulk buy order."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE bulk_buy_orders SET
                current_committed_units = ?,
                status = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            bulk_buy.current_committed_units,
            bulk_buy.status,
            bulk_buy.updated_at.isoformat(),
            bulk_buy.id,
        ))

        conn.commit()
        conn.close()
        return bulk_buy

    def get_bulk_buys_by_cell(self, cell_id: str) -> List[BulkBuyOrder]:
        """Get all bulk buys for a cell."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM bulk_buy_orders WHERE cell_id = ? ORDER BY created_at DESC",
            (cell_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_bulk_buy(row) for row in rows]

    def _row_to_bulk_buy(self, row: sqlite3.Row) -> BulkBuyOrder:
        """Convert database row to BulkBuyOrder model."""
        return BulkBuyOrder(
            id=row['id'],
            campaign_id=row['campaign_id'],
            item_name=row['item_name'],
            item_description=row['item_description'],
            unit=row['unit'],
            retail_price_per_unit=row['retail_price_per_unit'],
            wholesale_price_per_unit=row['wholesale_price_per_unit'],
            savings_percent=row['savings_percent'],
            minimum_units=row['minimum_units'],
            current_committed_units=row['current_committed_units'],
            cell_id=row['cell_id'],
            coordinator_id=row['coordinator_id'],
            supplier=row['supplier'],
            commitment_deadline=datetime.fromisoformat(row['commitment_deadline']),
            delivery_date=datetime.fromisoformat(row['delivery_date']),
            distribution_location=row['distribution_location'],
            status=row['status'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
        )

    # ===== Bulk Buy Commitments =====

    def create_bulk_buy_commitment(self, commitment: BulkBuyCommitment) -> BulkBuyCommitment:
        """Create a bulk buy commitment."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO bulk_buy_commitments (
                id, bulk_buy_id, user_id,
                units, total_cost,
                paid, picked_up,
                committed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            commitment.id,
            commitment.bulk_buy_id,
            commitment.user_id,
            commitment.units,
            commitment.total_cost,
            1 if commitment.paid else 0,
            1 if commitment.picked_up else 0,
            commitment.committed_at.isoformat(),
        ))

        conn.commit()
        conn.close()
        return commitment

    def get_bulk_buy_commitments(self, bulk_buy_id: str) -> List[BulkBuyCommitment]:
        """Get all commitments for a bulk buy."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM bulk_buy_commitments WHERE bulk_buy_id = ? ORDER BY committed_at DESC",
            (bulk_buy_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_bulk_buy_commitment(row) for row in rows]

    def _row_to_bulk_buy_commitment(self, row: sqlite3.Row) -> BulkBuyCommitment:
        """Convert database row to BulkBuyCommitment model."""
        return BulkBuyCommitment(
            id=row['id'],
            bulk_buy_id=row['bulk_buy_id'],
            user_id=row['user_id'],
            units=row['units'],
            total_cost=row['total_cost'],
            paid=bool(row['paid']),
            picked_up=bool(row['picked_up']),
            committed_at=datetime.fromisoformat(row['committed_at']),
        )
