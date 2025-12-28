"""
Node Configuration Service

Manages node-level configuration (separate from user accounts).
Stores config in data/node_config.json
"""

import os
import json
import secrets
from pathlib import Path
from typing import Optional
from app.models.node_config import NodeConfig, NodeConfigUpdate
import structlog

logger = structlog.get_logger()


class NodeConfigService:
    """Service for managing node configuration"""

    def __init__(self, config_path: str = "data/node_config.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config: Optional[NodeConfig] = None

    def is_configured(self) -> bool:
        """Check if node has been configured"""
        return self.config_path.exists()

    def get_config(self) -> Optional[NodeConfig]:
        """Get current node configuration"""
        if self._config:
            return self._config

        if not self.config_path.exists():
            return None

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self._config = NodeConfig(**data)
                return self._config
        except Exception as e:
            logger.error("config_load_failed", error=str(e))
            return None

    def create_config(self, config: NodeConfig) -> NodeConfig:
        """
        Create initial node configuration

        Raises:
            ValueError: If node is already configured
        """
        if self.is_configured():
            raise ValueError("Node is already configured")

        # Generate unique node ID if not provided
        if not config.node_id:
            config.node_id = f"node-{secrets.token_hex(8)}"

        # Validate mesh name (alphanumeric + hyphens only)
        if not config.mesh_name.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Mesh name must be alphanumeric (hyphens/underscores allowed)")

        # Save to disk
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config.model_dump(mode='json'), f, indent=2, default=str)

            self._config = config

            logger.info(
                "node_configured",
                mesh_name=config.mesh_fqdn,
                node_id=config.node_id,
                ai_enabled=config.enable_ai_inference,
                bridge_enabled=config.enable_bridge_mode,
            )

            # Also save to environment for other services
            self._save_to_env(config)

            return config

        except Exception as e:
            logger.error("config_save_failed", error=str(e))
            raise

    def update_config(self, updates: NodeConfigUpdate) -> NodeConfig:
        """
        Update node configuration

        Raises:
            ValueError: If node is not configured yet
        """
        current = self.get_config()
        if not current:
            raise ValueError("Node not configured - use create_config first")

        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)
        updated_config = current.model_copy(update=update_data)

        # Save
        try:
            with open(self.config_path, 'w') as f:
                json.dump(updated_config.model_dump(mode='json'), f, indent=2, default=str)

            self._config = updated_config
            self._save_to_env(updated_config)

            logger.info("node_config_updated", updates=list(update_data.keys()))
            return updated_config

        except Exception as e:
            logger.error("config_update_failed", error=str(e))
            raise

    def _save_to_env(self, config: NodeConfig):
        """Save key config values to .env file for other services"""
        env_path = Path(".env")

        # Read existing .env if it exists
        env_lines = []
        if env_path.exists():
            with open(env_path, 'r') as f:
                env_lines = [line for line in f.readlines()
                            if not line.startswith('MESH_NAME=')
                            and not line.startswith('COMMUNITY_NAME=')
                            and not line.startswith('NODE_ID=')]

        # Add our values
        env_lines.append(f"MESH_NAME={config.mesh_name}\n")
        if config.community_name:
            env_lines.append(f"COMMUNITY_NAME={config.community_name}\n")
        env_lines.append(f"NODE_ID={config.node_id}\n")

        # Write back
        with open(env_path, 'w') as f:
            f.writelines(env_lines)


# Singleton instance
_node_config_service: Optional[NodeConfigService] = None


def get_node_config_service() -> NodeConfigService:
    """Get node config service singleton"""
    global _node_config_service
    if _node_config_service is None:
        _node_config_service = NodeConfigService()
    return _node_config_service
