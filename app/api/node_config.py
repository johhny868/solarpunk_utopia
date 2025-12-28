"""
Node Configuration API

Handles initial node setup and configuration management.
"""

from fastapi import APIRouter, HTTPException
from app.models.node_config import NodeConfig, NodeConfigUpdate
from app.services.node_config_service import get_node_config_service
import structlog

logger = structlog.get_logger()

router = APIRouter(prefix="/node", tags=["node"])


@router.get("/config")
async def get_node_config():
    """
    Get current node configuration.

    Returns:
        NodeConfig if configured, None if not yet configured
    """
    service = get_node_config_service()
    config = service.get_config()

    if not config:
        return None

    return config


@router.get("/config/status")
async def get_config_status():
    """Check if node has been configured"""
    service = get_node_config_service()
    return {
        "configured": service.is_configured()
    }


@router.post("/config")
async def create_node_config(config: NodeConfig):
    """
    Create initial node configuration.

    This should only be called once during first-run setup.

    Raises:
        400: If node is already configured
        422: If validation fails
    """
    service = get_node_config_service()

    try:
        created_config = service.create_config(config)

        logger.info(
            "node_configured_via_api",
            mesh_name=created_config.mesh_fqdn,
            ai_enabled=created_config.enable_ai_inference,
            bridge_enabled=created_config.enable_bridge_mode,
        )

        return created_config

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("config_creation_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create configuration")


@router.put("/config")
async def update_node_config(updates: NodeConfigUpdate):
    """
    Update node configuration.

    Only provided fields will be updated.

    Raises:
        400: If node is not configured yet
        422: If validation fails
    """
    service = get_node_config_service()

    try:
        updated_config = service.update_config(updates)

        logger.info(
            "node_config_updated_via_api",
            mesh_name=updated_config.mesh_fqdn,
        )

        return updated_config

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("config_update_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update configuration")
