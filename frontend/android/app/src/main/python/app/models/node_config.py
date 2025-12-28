"""
Node Configuration Model

Stores configuration for this specific node/device.
This is set once during initial setup, before any users log in.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class NodeConfig(BaseModel):
    """Configuration for this mesh node"""

    # Identity
    mesh_name: str = Field(
        ...,
        description="Node name on .multiversemesh (e.g., 'alice', 'food-coop')"
    )
    community_name: Optional[str] = Field(
        None,
        description="Community subdomain (e.g., 'mycommunity' → alice.mycommunity.multiversemesh)"
    )
    node_description: Optional[str] = Field(
        None,
        description="What is this node for? (e.g., 'Personal device', 'Community hub')"
    )

    # Services
    enable_ai_inference: bool = Field(
        default=False,
        description="Share AI compute with the mesh"
    )
    enable_bridge_mode: bool = Field(
        default=False,
        description="Act as bridge between mesh islands"
    )

    # Contact
    admin_contact: Optional[str] = Field(
        None,
        description="Contact info for node operator (optional)"
    )

    # Metadata
    configured_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this node was configured"
    )
    node_id: Optional[str] = Field(
        None,
        description="Auto-generated unique node ID"
    )

    @property
    def mesh_fqdn(self) -> str:
        """Get full mesh name"""
        if self.community_name:
            return f"{self.mesh_name}.{self.community_name}.multiversemesh"
        return f"{self.mesh_name}.multiversemesh"


class NodeConfigUpdate(BaseModel):
    """Update node configuration"""

    mesh_name: Optional[str] = None
    community_name: Optional[str] = None
    node_description: Optional[str] = None
    enable_ai_inference: Optional[bool] = None
    enable_bridge_mode: Optional[bool] = None
    admin_contact: Optional[str] = None
