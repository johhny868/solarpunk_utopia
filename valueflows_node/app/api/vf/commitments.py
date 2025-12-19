"""Commitments API Endpoints - GAP-69"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional, List
import uuid

from ...models.vf.commitment import Commitment, CommitmentStatus
from ...database import get_database
from ...repositories.vf.commitment_repo import CommitmentRepository
from ...services.vf_bundle_publisher import VFBundlePublisher

router = APIRouter(prefix="/vf/commitments", tags=["commitments"])


@router.get("/", response_model=dict)
async def get_commitments(agent_id: str = None, status: str = None):
    """Get all commitments, optionally filtered by agent or status"""
    try:
        db = get_database()
        db.connect()
        commitment_repo = CommitmentRepository(db.conn)

        if agent_id:
            # Filter by agent
            status_enum = CommitmentStatus(status) if status else None
            commitments = commitment_repo.find_by_agent(agent_id, status_enum)
        else:
            # Get all commitments
            commitments = commitment_repo.find_all()
            # Filter by status if provided
            if status:
                commitments = [c for c in commitments if c.status.value == status]

        db.close()

        return {
            "commitments": [c.to_dict() for c in commitments],
            "count": len(commitments)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{commitment_id}", response_model=dict)
async def get_commitment(commitment_id: str):
    """Get a specific commitment"""
    try:
        db = get_database()
        db.connect()
        commitment_repo = CommitmentRepository(db.conn)

        commitment = commitment_repo.find_by_id(commitment_id)
        db.close()

        if not commitment:
            raise HTTPException(status_code=404, detail="Commitment not found")

        return commitment.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=dict)
async def create_commitment(commitment_data: dict):
    """Create a new commitment"""
    try:
        if "id" not in commitment_data:
            commitment_data["id"] = f"commitment:{uuid.uuid4()}"
        commitment_data["created_at"] = datetime.now().isoformat()

        commitment = Commitment.from_dict(commitment_data)

        db = get_database()
        db.connect()
        commitment_repo = CommitmentRepository(db.conn)
        created_commitment = commitment_repo.create(commitment)

        publisher = VFBundlePublisher()
        bundle = publisher.publish_vf_object(created_commitment, "Commitment")

        db.close()

        return {
            "status": "created",
            "commitment": created_commitment.to_dict(),
            "bundle_id": bundle["bundleId"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{commitment_id}", response_model=dict)
async def update_commitment(commitment_id: str, updates: dict):
    """Update a commitment's status"""
    try:
        db = get_database()
        db.connect()
        commitment_repo = CommitmentRepository(db.conn)

        commitment = commitment_repo.find_by_id(commitment_id)
        if not commitment:
            raise HTTPException(status_code=404, detail="Commitment not found")

        # Update status if provided
        if "status" in updates:
            commitment.status = CommitmentStatus(updates["status"])

        # Update fulfilled_by_event_id if provided
        if "fulfilled_by_event_id" in updates:
            commitment.fulfilled_by_event_id = updates["fulfilled_by_event_id"]

        updated_commitment = commitment_repo.update(commitment)

        publisher = VFBundlePublisher()
        bundle = publisher.publish_vf_object(updated_commitment, "Commitment")

        db.close()

        return {
            "status": "updated",
            "commitment": updated_commitment.to_dict(),
            "bundle_id": bundle["bundleId"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{commitment_id}", response_model=dict)
async def delete_commitment(commitment_id: str):
    """Delete a commitment"""
    try:
        db = get_database()
        db.connect()
        commitment_repo = CommitmentRepository(db.conn)

        commitment = commitment_repo.find_by_id(commitment_id)
        if not commitment:
            raise HTTPException(status_code=404, detail="Commitment not found")

        # TODO: Add ownership verification when auth is implemented

        commitment_repo.delete(commitment_id)
        db.close()

        return {
            "status": "deleted",
            "commitment_id": commitment_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
