"""
Agent Repository

CRUD operations for Agents.
"""

from typing import Optional, List
import sqlite3
from datetime import datetime

from ...models.vf.agent import Agent, AgentType, AgentStatus
from .base_repo import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    """Repository for Agent objects"""

    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "agents", Agent)

    def create(self, agent: Agent) -> Agent:
        """
        Create a new agent.

        Args:
            agent: Agent object

        Returns:
            Created agent
        """
        if agent.created_at is None:
            agent.created_at = datetime.now()

        query = """
            INSERT INTO agents (
                id, name, agent_type, description, image_url, primary_location_id,
                contact_info, status, status_note, status_updated_at,
                created_at, updated_at, author, signature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            agent.id,
            agent.name,
            agent.agent_type.value,
            agent.description,
            agent.image_url,
            agent.primary_location_id,
            agent.contact_info,
            agent.status.value,
            agent.status_note,
            agent.status_updated_at.isoformat() if agent.status_updated_at else None,
            agent.created_at.isoformat() if agent.created_at else None,
            agent.updated_at.isoformat() if agent.updated_at else None,
            agent.author,
            agent.signature,
        )

        self._execute(query, params)
        self.conn.commit()

        return agent

    def update(self, agent: Agent) -> Agent:
        """
        Update existing agent.

        Args:
            agent: Agent object

        Returns:
            Updated agent
        """
        agent.updated_at = datetime.now()

        query = """
            UPDATE agents SET
                name = ?,
                agent_type = ?,
                description = ?,
                image_url = ?,
                primary_location_id = ?,
                contact_info = ?,
                status = ?,
                status_note = ?,
                status_updated_at = ?,
                updated_at = ?
            WHERE id = ?
        """

        params = (
            agent.name,
            agent.agent_type.value,
            agent.description,
            agent.image_url,
            agent.primary_location_id,
            agent.contact_info,
            agent.status.value,
            agent.status_note,
            agent.status_updated_at.isoformat() if agent.status_updated_at else None,
            agent.updated_at.isoformat(),
            agent.id,
        )

        self._execute(query, params)
        self.conn.commit()

        return agent

    def find_by_type(self, agent_type: AgentType) -> List[Agent]:
        """Find agents by type"""
        query = "SELECT * FROM agents WHERE agent_type = ? ORDER BY name"
        rows = self._fetch_all(query, (agent_type.value,))
        return [Agent.from_dict(row) for row in rows]

    def find_by_name(self, name: str) -> List[Agent]:
        """Find agents by name (partial match)"""
        query = "SELECT * FROM agents WHERE name LIKE ? ORDER BY name"
        rows = self._fetch_all(query, (f"%{name}%",))
        return [Agent.from_dict(row) for row in rows]

    def update_status(self, agent_id: str, status: AgentStatus, status_note: Optional[str] = None) -> bool:
        """
        Update agent status (for rest mode).

        GAP-62: Loafer's Rights - Allow agents to signal they're taking a break.

        Args:
            agent_id: Agent ID
            status: New status (active, resting, sabbatical)
            status_note: Optional explanation

        Returns:
            True if updated, False if agent not found
        """
        query = """
            UPDATE agents SET
                status = ?,
                status_note = ?,
                status_updated_at = ?,
                updated_at = ?
            WHERE id = ?
        """

        now = datetime.now()
        params = (
            status.value,
            status_note,
            now.isoformat(),
            now.isoformat(),
            agent_id,
        )

        cursor = self._execute(query, params)
        self.conn.commit()

        return cursor.rowcount > 0

    def find_by_status(self, status: AgentStatus) -> List[Agent]:
        """
        Find agents by status.

        GAP-62: Used to find agents in rest mode, count community support needs, etc.

        Args:
            status: Status to filter by

        Returns:
            List of matching agents
        """
        query = "SELECT * FROM agents WHERE status = ? ORDER BY status_updated_at DESC"
        rows = self._fetch_all(query, (status.value,))
        return [Agent.from_dict(row) for row in rows]

    def count_in_rest_mode(self) -> int:
        """
        Count agents currently in rest mode (resting or sabbatical).

        GAP-62: For community stats - "23 people in rest mode (we're holding you)"
        """
        query = "SELECT COUNT(*) as count FROM agents WHERE status IN ('resting', 'sabbatical')"
        rows = self._fetch_all(query, ())
        return rows[0]['count'] if rows else 0
