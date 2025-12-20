"""
Counter-Power Agent

Automated immune system against centralized authority.

Key Features:
- Authority Audit: Detects power accumulation in hands of few
- Guild Filter: Distinguishes productive guilds from resource hoarders
- Leveling Protocols: Proposes remedies when hierarchy detected
- Safe Eject: Makes leaving/forking easy (voluntary association)

Based on proposal: openspec/changes/counter-power-agent/proposal.md
Inspired by Bakunin's anti-statism
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from .framework import BaseAgent, AgentConfig, Proposal, ProposalType


logger = logging.getLogger(__name__)

AGENT_VERSION = "1.0.0"


class CounterPowerAgent(BaseAgent):
    """
    Continuously audits the network for power asymmetry.

    This agent:
    1. Detects centralization (few people controlling decisions or resources)
    2. Distinguishes productive concentration from hoarding
    3. Alerts community to power accumulation
    4. Facilitates voluntary secession when needed
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        db_client: Optional[Any] = None,
        bundle_publisher: Optional[Any] = None,
        llm_client: Optional[Any] = None,
    ):
        super().__init__(
            agent_name="counter-power",
            config=config,
            db_client=db_client,
            bundle_publisher=bundle_publisher,
            llm_client=llm_client,
        )

    async def analyze(self) -> List[Proposal]:
        """
        Analyze power distribution and generate warnings/alerts.

        Returns:
            List of centralization warnings, warlord alerts, and pruning prompts
        """
        proposals = []

        # Check for governance centralization
        governance_centralization = await self._detect_governance_centralization()
        if governance_centralization:
            proposal = await self._create_centralization_warning(
                governance_centralization
            )
            proposals.append(proposal)

        # Check for resource hoarding (warlords)
        warlords = await self._detect_warlords()
        for warlord in warlords:
            proposal = await self._create_warlord_alert(warlord)
            proposals.append(proposal)

        # Check for passive/silent members who might want to leave
        silent_members = await self._detect_silent_members()
        for member in silent_members:
            proposal = await self._create_pruning_prompt(member)
            proposals.append(proposal)

        # Check for saboteurs (active blocking)
        saboteurs = await self._detect_saboteurs()
        for saboteur in saboteurs:
            proposal = await self._create_centralization_warning({
                "type": "saboteur",
                "user_id": saboteur["user_id"],
                "blocking_rate": saboteur["blocking_rate"],
            })
            proposals.append(proposal)

        return proposals

    async def _detect_governance_centralization(self) -> Optional[Dict[str, Any]]:
        """
        Detect if few people are making most decisions.

        Returns:
            Centralization data if detected, None otherwise
        """
        # TODO: Query proposal authorship and approval patterns
        # For now, return mock data

        return {
            "type": "governance",
            "user_id": "user:admindave",
            "role": "node_approver",
            "percentage_of_approvals": 80.0,
            "total_approvals": 120,
            "period_days": 30,
        }

    async def _detect_warlords(self) -> List[Dict[str, Any]]:
        """
        Detect resource hoarders (high stock, low outflow).

        Returns:
            List of warlord data
        """
        # TODO: Query resource inventory and flow patterns
        # For now, return mock data

        return [
            {
                "user_id": "user:resource_guy",
                "resource_type": "batteries",
                "stock_units": 500,
                "avg_weekly_outflow": 5,
                "inflow_rate": 50,  # Accumulating
                "guild_classification": "warlord",  # Not a productive guild
            },
        ]

    async def _detect_silent_members(self) -> List[Dict[str, Any]]:
        """
        Detect members with low activity who might want to leave.

        Returns:
            List of silent member data
        """
        # TODO: Query user activity patterns
        # For now, return mock data

        return [
            {
                "user_id": "user:quiet_bob",
                "days_since_last_activity": 45,
                "total_contributions": 2,
                "governance_participation": 0,
                "pattern": "silence",  # Not blocking, just not participating
            },
        ]

    async def _detect_saboteurs(self) -> List[Dict[str, Any]]:
        """
        Detect members who repeatedly block without explanation.

        Returns:
            List of saboteur data
        """
        # TODO: Query voting/blocking patterns
        # For now, return mock data

        return [
            {
                "user_id": "user:blocker",
                "total_blocks": 15,
                "total_votes": 20,
                "blocking_rate": 0.75,  # 75% of votes are blocks
                "blocks_with_explanation": 2,
                "pattern": "obstruction",
            },
        ]

    async def _create_centralization_warning(
        self,
        centralization: Dict[str, Any]
    ) -> Proposal:
        """
        Create a centralization warning proposal.

        Args:
            centralization: Centralization data

        Returns:
            Centralization warning proposal
        """
        user_id = centralization["user_id"]
        centralization_type = centralization["type"]

        if centralization_type == "governance":
            percentage = centralization["percentage_of_approvals"]
            role = centralization.get("role", "decision_maker")

            return Proposal(
                agent_name=self.agent_name,
                proposal_type=ProposalType.CENTRALIZATION_WARNING,
                title=f"Centralization warning: {user_id}",
                explanation=(
                    f"{user_id} is performing {percentage:.0f}% of {role} actions. "
                    f"This creates a Single Point of Need and risks hierarchy formation. "
                    f"Consider distributing this responsibility more widely or "
                    f"automating some decisions. This is not a punishment—it's a "
                    f"structural observation."
                ),
                inputs_used=[
                    f"approval_patterns:{role}:last_30_days",
                ],
                constraints=[
                    "Tone: Warning, not punishment",
                    "Community decides response",
                    "Recognize: This person may be helping, not power-seeking",
                ],
                data={
                    "user_id": user_id,
                    "centralization_type": centralization_type,
                    "percentage": percentage,
                    "role": role,
                    "period_days": centralization.get("period_days", 30),
                    "suggestions": [
                        "Rotate this role among multiple people",
                        "Create clear guidelines for others to learn this role",
                        "Automate routine decisions",
                        "Set term limits or rotation schedules",
                    ],
                },
                requires_approval=[],  # Warning only
            )

        elif centralization_type == "saboteur":
            blocking_rate = centralization["blocking_rate"]

            return Proposal(
                agent_name=self.agent_name,
                proposal_type=ProposalType.CENTRALIZATION_WARNING,
                title=f"Obstruction pattern detected: {user_id}",
                explanation=(
                    f"{user_id} is blocking {blocking_rate*100:.0f}% of proposals "
                    f"without providing explanations. This obstructs consensus. "
                    f"The community should discuss whether this pattern serves "
                    f"collective needs or personal grievances."
                ),
                inputs_used=[
                    f"voting_patterns:{user_id}:last_30_days",
                ],
                constraints=[
                    "Restorative: Seek to understand reasons",
                    "Community decides next steps",
                ],
                data={
                    "user_id": user_id,
                    "blocking_rate": blocking_rate,
                    "suggestions": [
                        "Initiate restorative circle",
                        "Request explanations for blocks",
                        "Offer voluntary secession option",
                    ],
                },
                requires_approval=[],
            )

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.CENTRALIZATION_WARNING,
            title=f"Centralization detected: {user_id}",
            explanation="Power asymmetry detected. Community review recommended.",
            inputs_used=["network_analysis"],
            constraints=[],
            data=centralization,
            requires_approval=[],
        )

    async def _create_warlord_alert(
        self,
        warlord: Dict[str, Any]
    ) -> Proposal:
        """
        Create a warlord alert proposal.

        Args:
            warlord: Warlord data

        Returns:
            Warlord alert proposal
        """
        user_id = warlord["user_id"]
        resource_type = warlord["resource_type"]
        stock = warlord["stock_units"]
        outflow = warlord["avg_weekly_outflow"]

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.WARLORD_ALERT,
            title=f"Resource hoarding detected: {resource_type}",
            explanation=(
                f"{user_id} has accumulated {stock} units of {resource_type} "
                f"but only circulates ~{outflow} units/week. "
                f"This looks like hoarding rather than productive guild formation. "
                f"A Battery Guild would have high stock AND high outflow. "
                f"Consider: Is this serving the commons or creating scarcity?"
            ),
            inputs_used=[
                f"inventory:{user_id}:{resource_type}",
                f"flow_patterns:{user_id}:{resource_type}",
            ],
            constraints=[
                "Guild distinction: High stock + high outflow = productive guild",
                "Warlord pattern: High stock + low outflow = hoarding",
                "Community decides response",
            ],
            data={
                "user_id": user_id,
                "resource_type": resource_type,
                "stock_units": stock,
                "avg_weekly_outflow": outflow,
                "inflow_rate": warlord.get("inflow_rate", 0),
                "classification": warlord["guild_classification"],
                "suggestions": [
                    "Request explanation for accumulation",
                    "Propose resource redistribution",
                    "Initiate governance discussion",
                ],
            },
            requires_approval=[],  # Alert only
        )

    async def _create_pruning_prompt(
        self,
        member: Dict[str, Any]
    ) -> Proposal:
        """
        Create a pruning prompt proposal (private check-in).

        Args:
            member: Silent member data

        Returns:
            Pruning prompt proposal
        """
        user_id = member["user_id"]
        days_inactive = member["days_since_last_activity"]

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.PRUNING_PROMPT,
            title=f"Check-in with inactive member: {user_id}",
            explanation=(
                f"{user_id} has been inactive for {days_inactive} days. "
                f"This might mean they're busy, or they might prefer to leave. "
                f"Send a private, supportive check-in: 'Do you want to stay? "
                f"Do you want to leave? Both are okay.' "
                f"Voluntary association means exit must be easy and stigma-free."
            ),
            inputs_used=[
                f"activity:{user_id}:last_90_days",
            ],
            constraints=[
                "Privacy: Private message, not public",
                "Supportive: Not a punishment",
                "Voluntary: Leaving is okay",
            ],
            data={
                "user_id": user_id,
                "days_inactive": days_inactive,
                "pattern": member.get("pattern", "silence"),
                "suggested_message": (
                    "Hey! We noticed you've been quiet lately. No judgment—life "
                    "happens. Just checking in: Do you want to stay in the network? "
                    "If you'd prefer to leave, that's totally okay and we can help "
                    "make that easy. What works for you?"
                ),
            },
            requires_approval=[
                "steward:community_care",  # Care steward sends the message
            ],
        )
