"""
Radical Inclusion Agent

Centers the margins and amplifies voices of the least connected.

Key Features:
- Marginality Check: Warns if proposals exclude least-connected nodes
- Conversational Excavation: Helps users discover and value invisible labor
- Care Work Recognition: Honors emotional labor and care work

Based on proposal: openspec/changes/radical-inclusion-agent/proposal.md
Inspired by bell hooks' "Love Ethic"
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .framework import BaseAgent, AgentConfig, Proposal, ProposalType


logger = logging.getLogger(__name__)

AGENT_VERSION = "1.0.0"


class RadicalInclusionAgent(BaseAgent):
    """
    Operationalizes love and inclusion through network topology analysis.

    This agent:
    1. Analyzes proposals for marginality impact (CI/CD for governance)
    2. Excavates invisible labor through conversational prompts
    3. Creates care work recognition proposals
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        db_client: Optional[Any] = None,
        bundle_publisher: Optional[Any] = None,
        llm_client: Optional[Any] = None,
    ):
        super().__init__(
            agent_name="radical-inclusion",
            config=config,
            db_client=db_client,
            bundle_publisher=bundle_publisher,
            llm_client=llm_client,
        )

    async def analyze(self) -> List[Proposal]:
        """
        Analyze network for exclusion and invisible labor.

        Returns:
            List of marginality warnings and care work recognition proposals
        """
        proposals = []

        # Check governance proposals for marginality impact
        governance_proposals = await self._get_pending_governance_proposals()
        for gov_proposal in governance_proposals:
            marginality_warning = await self._check_marginality_impact(gov_proposal)
            if marginality_warning:
                proposals.append(marginality_warning)

        # Recognize invisible care work
        care_work_instances = await self._detect_care_work()
        for care_work in care_work_instances:
            proposal = await self._create_care_work_recognition(care_work)
            proposals.append(proposal)

        return proposals

    async def _get_pending_governance_proposals(self) -> List[Dict[str, Any]]:
        """
        Get governance proposals that need marginality analysis.

        Returns:
            List of governance proposal data
        """
        # TODO: Query proposals database
        # For now, return mock data

        return [
            {
                "proposal_id": "prop:morning_meeting",
                "title": "Move community meeting to 9 AM",
                "type": "schedule_change",
                "impacts": [
                    "parents:morning_school_dropoff",
                    "night_shift_workers:sleep_schedule",
                ],
            },
        ]

    async def _check_marginality_impact(
        self,
        gov_proposal: Dict[str, Any]
    ) -> Optional[Proposal]:
        """
        Check if a governance proposal excludes marginalized groups.

        Args:
            gov_proposal: Governance proposal data

        Returns:
            Marginality warning proposal if impact detected, None otherwise
        """
        # Analyze who would be excluded
        excluded_groups = await self._identify_excluded_groups(gov_proposal)

        if not excluded_groups:
            return None

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.MARGINALITY_WARNING,
            title=f"Marginality warning: {gov_proposal['title']}",
            explanation=(
                f"The proposal '{gov_proposal['title']}' may exclude "
                f"{len(excluded_groups)} group(s): "
                f"{', '.join(excluded_groups)}. "
                f"Consider adjusting to be more inclusive or providing "
                f"alternative participation methods."
            ),
            inputs_used=[
                f"proposal:{gov_proposal['proposal_id']}",
                "network_topology:connection_patterns",
                "user_availability:historical",
            ],
            constraints=[
                "Privacy: Groups reported anonymously (k-anonymity)",
                "Actionable: Include specific suggestions for inclusion",
            ],
            data={
                "original_proposal_id": gov_proposal["proposal_id"],
                "excluded_groups": excluded_groups,
                "impact_type": "temporal_exclusion",
                "suggestions": [
                    "Offer async participation option",
                    "Record meeting for later viewing",
                    "Schedule multiple time slots",
                    "Use lazy consensus for this decision",
                ],
            },
            requires_approval=[],  # Warning only, no approval needed
        )

    async def _identify_excluded_groups(
        self,
        gov_proposal: Dict[str, Any]
    ) -> List[str]:
        """
        Identify which groups would be excluded by a proposal.

        Args:
            gov_proposal: Governance proposal data

        Returns:
            List of excluded group names (anonymized)
        """
        # TODO: Analyze network topology and user availability
        # Use k-anonymity to protect privacy
        # For now, return mock data

        if "9 AM" in gov_proposal.get("title", ""):
            return [
                "Anonymous Group 1 (parents)",
                "Anonymous Group 2 (night shift workers)",
            ]

        return []

    async def _detect_care_work(self) -> List[Dict[str, Any]]:
        """
        Detect instances of invisible care work.

        Returns:
            List of care work instances
        """
        # TODO: Use conversational excavation logs
        # For now, return mock data

        return [
            {
                "user_id": "user:alice",
                "care_type": "emotional_support",
                "description": "Talked Dave down from panic",
                "hours_estimated": 2.0,
                "discovered_via": "evening_checkin",
                "timestamp": datetime.now(timezone.utc),
            },
            {
                "user_id": "user:bob",
                "care_type": "conflict_mediation",
                "description": "Helped resolve dispute between neighbors",
                "hours_estimated": 1.5,
                "discovered_via": "conversational_excavation",
                "timestamp": datetime.now(timezone.utc),
            },
        ]

    async def _create_care_work_recognition(
        self,
        care_work: Dict[str, Any]
    ) -> Proposal:
        """
        Create a care work recognition proposal.

        Args:
            care_work: Care work instance data

        Returns:
            Care work recognition proposal
        """
        user_id = care_work["user_id"]
        care_type = care_work["care_type"]
        description = care_work["description"]
        hours = care_work["hours_estimated"]

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.CARE_WORK_RECOGNITION,
            title=f"Recognize care work by {user_id}",
            explanation=(
                f"{user_id} provided {care_type} ({description}). "
                f"This care work (est. {hours} hours) is vital to community "
                f"well-being but often goes unrecognized. Let's honor this "
                f"contribution and ensure it's visible in the gift flow."
            ),
            inputs_used=[
                f"conversational_excavation:{user_id}",
            ],
            constraints=[
                "Consent: User must approve before public recognition",
                "Privacy: Can be recognized anonymously if preferred",
                "Non-transactional: Recognition, not payment",
            ],
            data={
                "user_id": user_id,
                "care_type": care_type,
                "description": description,
                "hours_estimated": hours,
                "visibility": "public",  # Can be changed to "anonymous"
                "recognition_type": "gift_energy_acknowledgment",
            },
            requires_approval=[
                user_id,  # User must consent to recognition
            ],
        )

    async def _conversational_excavation(
        self,
        user_id: str,
        user_response: str
    ) -> Optional[Dict[str, Any]]:
        """
        Excavate invisible labor through conversation.

        This would be called by the UI when users say "I did nothing today".

        Args:
            user_id: User ID
            user_response: User's initial response to "What did you do today?"

        Returns:
            Care work data if discovered, None otherwise
        """
        # TODO: Use LLM to parse user responses and detect care work
        # Prompts like:
        # - "Did you hold space for anyone?"
        # - "Did you rest? Resting is resistance."
        # - "Did you counsel a friend?"

        # For now, return mock detection
        if "nothing" in user_response.lower():
            return {
                "user_id": user_id,
                "care_type": "emotional_support",
                "description": "Likely provided support not yet recognized",
                "needs_follow_up": True,
            }

        return None
