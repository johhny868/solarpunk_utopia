"""Knowledge Osmosis API

Study circles share learning artifacts.

'Knowledge emerges only through invention and re-invention.' - Paulo Freire
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime

from app.services.knowledge_osmosis_service import KnowledgeOsmosisService
from app.models.knowledge_osmosis import ArtifactType
from app.auth.middleware import get_current_user

router = APIRouter(prefix="/api/knowledge-osmosis", tags=["knowledge-osmosis"])


class CreateCircleRequest(BaseModel):
    """Create a study circle."""
    name: str
    topic: str
    description: str
    artifact_commitment: str


class PublishArtifactRequest(BaseModel):
    """Publish a learning artifact."""
    circle_id: str
    title: str
    artifact_type: ArtifactType
    content: str
    topic: str
    tags: List[str]
    difficulty: str = 'beginner'
    description: str = None


class ArtifactResponse(BaseModel):
    """Learning artifact response."""
    id: str
    title: str
    topic: str
    artifact_type: str
    difficulty: str
    tags: List[str]
    view_count: int
    use_count: int
    published_at: datetime


def get_service() -> KnowledgeOsmosisService:
    return KnowledgeOsmosisService(db_path="data/dtn_bundles.db")


@router.post("/circle")
async def create_circle(
    request: CreateCircleRequest,
    current_user: dict = Depends(get_current_user),
    service: KnowledgeOsmosisService = Depends(get_service)
):
    """Create a study circle."""
    circle = service.create_study_circle(
        name=request.name,
        topic=request.topic,
        description=request.description,
        created_by=current_user["id"],
        artifact_commitment=request.artifact_commitment
    )
    return {"circle_id": circle.id}


@router.post("/artifact")
async def publish_artifact(
    request: PublishArtifactRequest,
    current_user: dict = Depends(get_current_user),
    service: KnowledgeOsmosisService = Depends(get_service)
):
    """Publish a learning artifact to the Common Heap."""
    artifact = service.publish_artifact(
        circle_id=request.circle_id,
        created_by_user_id=current_user["id"],
        title=request.title,
        artifact_type=request.artifact_type,
        content=request.content,
        topic=request.topic,
        tags=request.tags,
        difficulty=request.difficulty,
        description=request.description
    )
    return {"artifact_id": artifact.id}


@router.get("/discover/{topic}", response_model=List[ArtifactResponse])
async def discover_artifacts(
    topic: str,
    service: KnowledgeOsmosisService = Depends(get_service)
):
    """Discover artifacts by topic."""
    artifacts = service.discover_artifacts(topic)
    return [
        ArtifactResponse(
            id=a.id,
            title=a.title,
            topic=a.topic,
            artifact_type=a.artifact_type.value,
            difficulty=a.difficulty,
            tags=a.tags,
            view_count=a.view_count,
            use_count=a.use_count,
            published_at=a.published_at
        )
        for a in artifacts
    ]
