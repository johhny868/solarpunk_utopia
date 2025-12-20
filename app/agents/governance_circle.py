"""
Governance Circle Agent

Facilitates human-AI collaboration in decision-making and conflict resolution.

Key Features:
- Loomio-lite proposal flow (humans AND AI can propose)
- Restorative justice circles for conflict resolution
- Consensus health monitoring to prevent stagnocracy

Based on proposal: openspec/changes/governance-circle-agent/proposal.md
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .framework import BaseAgent, AgentConfig, Proposal, ProposalType


logger = logging.getLogger(__name__)

AGENT_VERSION = "1.0.0"


class GovernanceCircleAgent(BaseAgent):
    """
    Facilitates decentralized governance and conflict resolution.

    This agent:
    1. Creates proposals based on data (e.g., "Predicted shortfall")
    2. Facilitates restorative justice circles for conflicts
    3. Monitors consensus health to prevent stagnation
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        db_client: Optional[Any] = None,
        bundle_publisher: Optional[Any] = None,
        llm_client: Optional[Any] = None,
    ):
        super().__init__(
            agent_name="governance-circle",
            config=config,
            db_client=db_client,
            bundle_publisher=bundle_publisher,
            llm_client=llm_client,
        )

    async def analyze(self) -> List[Proposal]:
        """
        Analyze governance needs and generate proposals.

        Returns:
            List of governance proposals and mediation requests
        """
        proposals = []

        # Check for conflicts that need mediation
        conflicts = await self._get_unresolved_conflicts()
        for conflict in conflicts:
            proposal = await self._create_mediation_request(conflict)
            proposals.append(proposal)

        # Check for data-driven governance needs (e.g., resource shortfalls)
        governance_needs = await self._detect_governance_needs()
        for need in governance_needs:
            proposal = await self._create_governance_proposal(need)
            proposals.append(proposal)

        # Monitor consensus health
        consensus_issues = await self._check_consensus_health()
        for issue in consensus_issues:
            proposal = await self._create_governance_proposal(issue)
            proposals.append(proposal)

        return proposals

    async def _get_unresolved_conflicts(self) -> List[Dict[str, Any]]:
        """
        Get conflicts that need mediation (e.g., user blocks).

        Returns:
            List of conflict data
        """
        # TODO: Query database for user blocks and conflict reports
        # For now, return mock data

        return [
            {
                "user_a": "user:alice",
                "user_b": "user:bob",
                "block_type": "block",
                "timestamp": datetime.now(timezone.utc),
                "reason": "Communication breakdown",
            },
        ]

    async def _detect_governance_needs(self) -> List[Dict[str, Any]]:
        """
        Detect situations requiring governance decisions.

        Returns:
            List of governance needs
        """
        # TODO: Query for resource shortfalls, budget decisions, etc.
        # For now, return mock data

        return [
            {
                "type": "resource_shortfall",
                "resource": "firewood",
                "predicted_days_until_empty": 10,
                "severity": "high",
            },
        ]

    async def _check_consensus_health(self) -> List[Dict[str, Any]]:
        """
        Check if governance is healthy or stagnant.

        Returns:
            List of consensus health issues
        """
        # TODO: Query voting patterns to detect low engagement
        # For now, return mock data

        return [
            {
                "type": "low_engagement",
                "recent_proposals": 5,
                "avg_voters_per_proposal": 3,
                "total_community_members": 50,
                "engagement_rate": 0.06,  # Only 6% voting
            },
        ]

    async def _create_mediation_request(
        self,
        conflict: Dict[str, Any]
    ) -> Proposal:
        """
        Create a mediation request proposal.

        Args:
            conflict: Conflict data

        Returns:
            Mediation request proposal
        """
        user_a = conflict["user_a"]
        user_b = conflict["user_b"]

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.MEDIATION_REQUEST,
            title=f"Mediation request: {user_a} <-> {user_b}",
            explanation=(
                f"A conflict has been detected between {user_a} and {user_b}. "
                f"A restorative justice circle is recommended to facilitate "
                f"resolution. Pre-selected mediators will be invited to help "
                f"both parties find common ground."
            ),
            inputs_used=[
                f"block_event:{user_a}:{user_b}",
            ],
            constraints=[
                "Privacy: Circle details kept confidential",
                "Timing: Schedule within 7 days",
                "Voluntary: Both parties must consent",
            ],
            data={
                "user_a": user_a,
                "user_b": user_b,
                "conflict_type": conflict.get("block_type", "unknown"),
                "timestamp": conflict["timestamp"].isoformat(),
                "suggested_mediators": [
                    "mediator:carol",
                    "mediator:dave",
                ],
                "circle_format": "restorative_justice",
            },
            requires_approval=[
                user_a,
                user_b,
                "mediator:carol",  # At least one mediator must approve
            ],
        )

    async def _create_governance_proposal(
        self,
        need: Dict[str, Any]
    ) -> Proposal:
        """
        Create a governance proposal based on detected need.

        Args:
            need: Governance need data

        Returns:
            Governance proposal
        """
        need_type = need["type"]

        if need_type == "resource_shortfall":
            resource = need["resource"]
            days_left = need["predicted_days_until_empty"]

            return Proposal(
                agent_name=self.agent_name,
                proposal_type=ProposalType.GOVERNANCE_PROPOSAL,
                title=f"Address {resource} shortfall",
                explanation=(
                    f"Predictive analysis shows {resource} will run out in "
                    f"{days_left} days. The community needs to decide: "
                    f"Should we ration, source more, or find alternatives?"
                ),
                inputs_used=[
                    f"inventory:{resource}",
                    f"consumption_history:{resource}",
                ],
                constraints=[
                    "Timing: Decision needed before shortfall occurs",
                    "Impact: Affects all community members",
                ],
                data={
                    "proposal_type": "resource_management",
                    "resource": resource,
                    "days_until_shortfall": days_left,
                    "options": [
                        "Implement rationing",
                        "Source more externally",
                        "Find alternative resources",
                    ],
                    "voting_deadline": (
                        datetime.now(timezone.utc) + timedelta(days=days_left - 2)
                    ).isoformat(),
                },
                requires_approval=[
                    "community:lazy_consensus",  # Lazy consensus: silence = assent
                ],
            )

        elif need_type == "low_engagement":
            engagement_rate = need["engagement_rate"]

            return Proposal(
                agent_name=self.agent_name,
                proposal_type=ProposalType.GOVERNANCE_PROPOSAL,
                title="Address low governance engagement",
                explanation=(
                    f"Only {engagement_rate*100:.0f}% of community members are "
                    f"participating in governance decisions. This risks creating "
                    f"hidden power structures. Should we adjust our governance "
                    f"process to be more accessible?"
                ),
                inputs_used=[
                    "voting_patterns:last_30_days",
                ],
                constraints=[
                    "Goal: Increase engagement without creating bureaucracy",
                ],
                data={
                    "proposal_type": "process_improvement",
                    "current_engagement_rate": engagement_rate,
                    "target_engagement_rate": 0.3,  # 30%
                    "suggestions": [
                        "Simplify voting interface",
                        "Use lazy consensus for minor decisions",
                        "Create clearer proposal summaries",
                        "Schedule decision-making gatherings",
                    ],
                },
                requires_approval=[
                    "community:lazy_consensus",
                ],
            )

        # Default generic proposal
        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.GOVERNANCE_PROPOSAL,
            title=f"Governance decision needed: {need_type}",
            explanation=f"The agent has detected a governance need: {need}",
            inputs_used=["agent_analysis"],
            constraints=[],
            data=need,
            requires_approval=["community:lazy_consensus"],
        )
