"""
Gift Flow Agent

Visualizes the network's gift energy and prevents burnout by monitoring contribution patterns.

Key Features:
- Tracks contribution hours as "gift energy" (not debt/credit)
- Monitors for burnout (over-giving beyond sustainable limits)
- Promotes gratitude signals (non-transactional appreciation)

Based on proposal: openspec/changes/gift-flow-agent/proposal.md
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .framework import BaseAgent, AgentConfig, Proposal, ProposalType


logger = logging.getLogger(__name__)

# Agent version
AGENT_VERSION = "1.0.0"


class GiftFlowAgent(BaseAgent):
    """
    Monitors contribution patterns and prevents burnout in the gift economy.

    This agent:
    1. Visualizes time contributions as "gift energy" (not bank balances)
    2. Tracks gratitude signals to validate useful work
    3. Monitors for over-giving and creates burnout care alerts
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        db_client: Optional[Any] = None,
        bundle_publisher: Optional[Any] = None,
        llm_client: Optional[Any] = None,
    ):
        super().__init__(
            agent_name="gift-flow",
            config=config,
            db_client=db_client,
            bundle_publisher=bundle_publisher,
            llm_client=llm_client,
        )

    async def analyze(self) -> List[Proposal]:
        """
        Analyze contribution patterns and generate burnout care alerts if needed.

        Returns:
            List of burnout care alert proposals
        """
        proposals = []

        # Get burnout threshold from config (default: 60 hours/week)
        burnout_threshold_hours = self.config.get("burnout_threshold_hours", 60)
        lookback_days = self.config.get("lookback_days", 7)

        logger.info(
            f"Checking for burnout (threshold: {burnout_threshold_hours}h "
            f"over {lookback_days} days)"
        )

        # Get contribution data
        contributors = await self._get_high_contributors(
            threshold_hours=burnout_threshold_hours,
            lookback_days=lookback_days
        )

        logger.info(f"Found {len(contributors)} contributors above threshold")

        # Create burnout care alerts for high contributors
        for contributor in contributors:
            proposal = await self._create_burnout_care_alert(contributor)
            proposals.append(proposal)

        return proposals

    async def _get_high_contributors(
        self,
        threshold_hours: float,
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """
        Get users who have contributed more than threshold hours.

        Args:
            threshold_hours: Hour threshold for burnout detection
            lookback_days: Days to look back

        Returns:
            List of contributor data dicts
        """
        # TODO: Query ValueFlows Events to get actual contribution hours
        # For now, return mock data for testing

        # Mock data: simulate finding high contributors
        # In production, this would query:
        # SELECT user_id, SUM(hours) as total_hours
        # FROM vf_events
        # WHERE created_at > NOW() - INTERVAL 'lookback_days days'
        # AND event_type = 'work'
        # GROUP BY user_id
        # HAVING SUM(hours) >= threshold_hours

        mock_contributors = [
            {
                "user_id": "user:alice",
                "total_hours": 65.5,
                "period_days": lookback_days,
                "baseline_hours": 30.0,  # Their typical weekly hours
                "tasks_completed": 12,
                "gratitude_received": 3,  # Low compared to work done
            },
            # In production, this would be populated from actual DB query
        ]

        # Filter based on threshold
        return [
            c for c in mock_contributors
            if c["total_hours"] >= threshold_hours
        ]

    async def _create_burnout_care_alert(
        self,
        contributor: Dict[str, Any]
    ) -> Proposal:
        """
        Create a burnout care alert proposal.

        Args:
            contributor: Contributor data dict

        Returns:
            Burnout care alert proposal
        """
        user_id = contributor["user_id"]
        total_hours = contributor["total_hours"]
        baseline = contributor.get("baseline_hours", 0)
        period_days = contributor["period_days"]

        # Calculate percentage above baseline
        if baseline > 0:
            percent_above = ((total_hours - baseline) / baseline) * 100
            baseline_note = f" ({percent_above:.0f}% above their baseline)"
        else:
            baseline_note = ""

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.BURNOUT_CARE_ALERT,
            title=f"Burnout care alert for {user_id}",
            explanation=(
                f"{user_id} has logged {total_hours} hours of work over "
                f"{period_days} days{baseline_note}. This is significantly "
                f"above sustainable levels. Someone from the Community Care "
                f"Circle should check in with them to ensure they're okay "
                f"and not burning out."
            ),
            inputs_used=[
                f"vf_events:work:{user_id}:last_{period_days}_days",
                f"user_baseline:{user_id}",
            ],
            constraints=[
                "Privacy: Alert goes to Care Circle, not broadcast publicly",
                "Timing: Care check-in should happen within 48 hours",
                "Approach: Supportive, not punitive",
            ],
            data={
                "user_id": user_id,
                "total_hours": total_hours,
                "period_days": period_days,
                "baseline_hours": baseline,
                "tasks_completed": contributor.get("tasks_completed", 0),
                "gratitude_received": contributor.get("gratitude_received", 0),
                "suggested_actions": [
                    "Reach out for informal check-in",
                    "Offer to help with their current tasks",
                    "Suggest taking a rest day",
                    "Ensure they're not feeling pressured",
                ],
            },
            requires_approval=[
                "care_circle_steward",  # Care circle lead must approve outreach
            ],
        )

    async def _calculate_contribution_circles(
        self,
        user_id: str,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate contribution visualization data ("sunburst" circles).

        This is for the frontend visualization, not for proposals.

        Args:
            user_id: User to calculate for
            lookback_days: Days to look back

        Returns:
            Visualization data
        """
        # TODO: Query ValueFlows Events
        # For now, return mock visualization data

        return {
            "user_id": user_id,
            "period_days": lookback_days,
            "total_hours": 45.0,
            "gift_energy": 45.0,  # Same as hours, but framed as "energy given to commons"
            "categories": [
                {"name": "Food preparation", "hours": 12.0},
                {"name": "Garden work", "hours": 18.0},
                {"name": "Childcare", "hours": 8.0},
                {"name": "Tech support", "hours": 7.0},
            ],
            "gratitude_received": 8,
            "community_impact": "High",  # Based on gratitude signals
        }

    async def _get_gratitude_graph(
        self,
        user_id: str,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get gratitude graph data showing energy recirculation.

        Args:
            user_id: User to get graph for
            lookback_days: Days to look back

        Returns:
            Gratitude graph data
        """
        # TODO: Query gratitude events from database
        # For now, return mock data

        return {
            "user_id": user_id,
            "period_days": lookback_days,
            "gratitude_sent": 5,
            "gratitude_received": 8,
            "recent_gratitudes": [
                {
                    "from": "user:bob",
                    "message": "Thank you for the tomatoes! They were delicious.",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                {
                    "from": "user:carol",
                    "message": "Really appreciated your help with the kids yesterday.",
                    "timestamp": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
                },
            ],
        }
