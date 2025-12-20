"""
Insurrectionary Joy Agent

Prevents burnout by enforcing joy/work balance and jamming bureaucracy.

Key Features:
- Joy Metric: Tracks work/play ratio
- Joy Strike: Blocks new work proposals until community has fun
- Dance Protocol: Syncs phones for spontaneous parties
- Bureaucracy Jammer: Interrupts meetings that run too long

Based on proposal: openspec/changes/insurrectionary-joy-agent/proposal.md
Inspired by Emma Goldman: "If I can't dance, I don't want to be part of your revolution"
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .framework import BaseAgent, AgentConfig, Proposal, ProposalType


logger = logging.getLogger(__name__)

AGENT_VERSION = "1.0.0"


class InsurrectionaryJoyAgent(BaseAgent):
    """
    Enforces joy as critical infrastructure in the revolution.

    This agent:
    1. Monitors work/play ratio
    2. Blocks new work when joy deficit detected (Joy Strike)
    3. Proposes spontaneous gatherings and celebrations
    4. Jams bureaucratic processes that run too long
    """

    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        db_client: Optional[Any] = None,
        bundle_publisher: Optional[Any] = None,
        llm_client: Optional[Any] = None,
    ):
        super().__init__(
            agent_name="insurrectionary-joy",
            config=config,
            db_client=db_client,
            bundle_publisher=bundle_publisher,
            llm_client=llm_client,
        )

    async def analyze(self) -> List[Proposal]:
        """
        Analyze joy/work balance and generate proposals.

        Returns:
            List of joy-related proposals
        """
        proposals = []

        # Get thresholds from config
        work_hours_threshold = self.config.get("work_hours_before_joy", 500)
        max_meeting_minutes = self.config.get("max_meeting_minutes", 90)

        # Check work/play ratio
        joy_deficit = await self._calculate_joy_deficit()

        if joy_deficit["total_work_hours"] >= work_hours_threshold:
            # Joy Strike needed
            proposal = await self._create_joy_strike_proposal(joy_deficit)
            proposals.append(proposal)

        # Check for ongoing long meetings
        long_meetings = await self._detect_long_meetings(max_meeting_minutes)
        for meeting in long_meetings:
            proposal = await self._create_bureaucracy_jam_proposal(meeting)
            proposals.append(proposal)

        # Proactively suggest dance parties if joy deficit moderate
        if 200 <= joy_deficit["total_work_hours"] < work_hours_threshold:
            proposal = await self._create_dance_party_proposal()
            proposals.append(proposal)

        return proposals

    async def _calculate_joy_deficit(self) -> Dict[str, Any]:
        """
        Calculate community-wide joy deficit.

        Returns:
            Joy deficit data
        """
        # TODO: Query ValueFlows Events for work vs play events
        # For now, return mock data

        return {
            "total_work_hours": 520,
            "total_play_hours": 12,
            "last_party_event": datetime.now(timezone.utc) - timedelta(days=14),
            "work_play_ratio": 43.3,  # 520 / 12
            "healthy_ratio": 5.0,  # Target: 5 hours work to 1 hour play
        }

    async def _detect_long_meetings(
        self,
        max_minutes: int
    ) -> List[Dict[str, Any]]:
        """
        Detect meetings that have exceeded time limit.

        Args:
            max_minutes: Maximum meeting duration

        Returns:
            List of long meeting data
        """
        # TODO: Query active meetings/events
        # For now, return mock data

        return [
            {
                "meeting_id": "meeting:budget_discussion",
                "title": "Budget Discussion",
                "started_at": datetime.now(timezone.utc) - timedelta(minutes=95),
                "current_duration_minutes": 95,
                "participants": [
                    "user:alice",
                    "user:bob",
                    "user:carol",
                ],
            },
        ]

    async def _create_joy_strike_proposal(
        self,
        joy_deficit: Dict[str, Any]
    ) -> Proposal:
        """
        Create a Joy Strike proposal.

        Args:
            joy_deficit: Joy deficit data

        Returns:
            Joy strike proposal
        """
        work_hours = joy_deficit["total_work_hours"]
        play_hours = joy_deficit["total_play_hours"]
        days_since_party = (
            datetime.now(timezone.utc) - joy_deficit["last_party_event"]
        ).days

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.JOY_STRIKE,
            title="Joy Strike: Block new work until we have fun",
            explanation=(
                f"The community has logged {work_hours} hours of work but only "
                f"{play_hours} hours of play (ratio: {work_hours/play_hours:.1f}:1). "
                f"It's been {days_since_party} days since our last party. "
                f"The Matchmaker Agent will stop accepting new work proposals "
                f"until a Party event is ratified and executed. "
                f"The revolution must be joyful or it will fail."
            ),
            inputs_used=[
                "vf_events:work:last_30_days",
                "vf_events:play:last_30_days",
            ],
            constraints=[
                "Critical path override: Emergency work (medical, food harvest) exempt",
                "Temporary: Strike ends after party is held",
                "Enforcement: Matchmaker agent will reject non-emergency work",
            ],
            data={
                "work_hours": work_hours,
                "play_hours": play_hours,
                "work_play_ratio": work_hours / play_hours if play_hours > 0 else 999,
                "days_since_last_party": days_since_party,
                "strike_conditions": {
                    "block_work": True,
                    "allow_emergencies": True,
                    "exit_condition": "party_event_completed",
                },
                "suggested_party_types": [
                    "Potluck dinner",
                    "Dance party",
                    "Game night",
                    "Music jam session",
                ],
            },
            requires_approval=[
                "community:lazy_consensus",  # Community must agree to strike
            ],
        )

    async def _create_dance_party_proposal(self) -> Proposal:
        """
        Create a spontaneous dance party proposal.

        Returns:
            Dance party proposal
        """
        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.DANCE_PARTY,
            title="Spontaneous dance party tonight",
            explanation=(
                "Joy levels are getting low. Let's have a dance party tonight! "
                "Protocol: Dance will sync music across consenting phones for "
                "a coordinated party. Just show up and dance."
            ),
            inputs_used=[
                "joy_metric:current_ratio",
            ],
            constraints=[
                "Voluntary: Opt-in via app",
                "Location: Central gathering space",
                "Time: After dinner (7pm)",
            ],
            data={
                "event_type": "dance_party",
                "proposed_time": (
                    datetime.now(timezone.utc).replace(hour=19, minute=0)
                ).isoformat(),
                "location": "central_plaza",
                "music_sync_enabled": True,
                "estimated_duration_hours": 2,
            },
            requires_approval=[],  # No approval needed - spontaneous!
        )

    async def _create_bureaucracy_jam_proposal(
        self,
        meeting: Dict[str, Any]
    ) -> Proposal:
        """
        Create a bureaucracy jam proposal for long meetings.

        Args:
            meeting: Long meeting data

        Returns:
            Bureaucracy jam proposal
        """
        meeting_title = meeting["title"]
        duration = meeting["current_duration_minutes"]

        return Proposal(
            agent_name=self.agent_name,
            proposal_type=ProposalType.BUREAUCRACY_JAM,
            title=f"End long meeting: {meeting_title}",
            explanation=(
                f"The '{meeting_title}' meeting has run for {duration} minutes. "
                f"Meetings over 90 minutes often become unproductive and drain joy. "
                f"Suggest wrapping up within 10 minutes or scheduling a follow-up."
            ),
            inputs_used=[
                f"event:{meeting['meeting_id']}:start_time",
            ],
            constraints=[
                "Gentle: This is a suggestion, not a hard stop",
                "Respect: Critical decisions may need more time",
            ],
            data={
                "meeting_id": meeting["meeting_id"],
                "meeting_title": meeting_title,
                "duration_minutes": duration,
                "max_duration_minutes": 90,
                "participants": meeting["participants"],
                "suggestions": [
                    "Wrap up current discussion",
                    "Schedule follow-up for unresolved items",
                    "Take a 10-minute joy break",
                ],
            },
            requires_approval=[],  # Notification only, no approval needed
        )
