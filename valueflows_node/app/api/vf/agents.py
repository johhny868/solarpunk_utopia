"""
Agents API Endpoints

POST /vf/agents - Create agent
GET /vf/agents - List agents
GET /vf/agents/{id} - Get agent
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
import uuid

from ...models.vf.agent import Agent, AgentType
from ...models.requests.vf_objects import AgentCreate
from ...database import get_database
from ...repositories.vf.agent_repo import AgentRepository
from ...services.signing_service import SigningService

router = APIRouter(prefix="/vf/agents", tags=["agents"])


@router.post("", response_model=dict)
async def create_agent(agent_data: AgentCreate):
    """
    Create a new agent.

    GAP-43: Now uses Pydantic validation model.

    Validates:
    - Required fields present (name)
    - Field types correct
    - String lengths reasonable
    - URLs have valid format
    """
    try:
        # Convert validated Pydantic model to dict
        data = agent_data.model_dump()

        # Generate ID
        data["id"] = f"agent:{uuid.uuid4()}"

        # Set timestamps
        data["created_at"] = datetime.now().isoformat()

        # Map fields: "note" -> note is already correct in Pydantic model
        # No mapping needed for agent create

        # Create Agent object
        agent = Agent.from_dict(data)

        # Sign the agent
        # Use the node's signing service
        signer = SigningService()
        signer.sign_and_update(agent, agent.id)

        # Save to database
        db = get_database()
        db.connect()
        agent_repo = AgentRepository(db.conn)
        created_agent = agent_repo.create(agent)
        db.close()

        return created_agent.to_dict()

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=dict)
async def list_agents(
    agent_type: Optional[str] = Query(None, description="Filter by type: person, group, or place"),
    name: Optional[str] = Query(None, description="Filter by name (partial match)"),
    limit: int = Query(100, description="Maximum results")
):
    """
    List agents with filters.

    Query parameters:
    - agent_type: Filter by type ("person", "group", or "place")
    - name: Filter by name (partial match)
    - limit: Maximum results
    """
    try:
        db = get_database()
        db.connect()
        agent_repo = AgentRepository(db.conn)

        # Apply filters
        if agent_type:
            agent_type_enum = AgentType(agent_type)
            agents = agent_repo.find_by_type(agent_type_enum)
        elif name:
            agents = agent_repo.find_by_name(name)
        else:
            agents = agent_repo.find_all(limit=limit)

        db.close()

        return {
            "agents": [a.to_dict() for a in agents],
            "count": len(agents)
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{agent_id}", response_model=dict)
async def get_agent(agent_id: str):
    """Get agent by ID"""
    try:
        db = get_database()
        db.connect()
        agent_repo = AgentRepository(db.conn)
        agent = agent_repo.find_by_id(agent_id)
        db.close()

        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        return agent.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
