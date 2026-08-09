"""
SwarmPersistence manager for persisting swarm campaign JSON manifests under outputs/swarms/.
"""

import json
import logging
from pathlib import Path
from uuid import UUID
from typing import Dict, Any, List

from swarm.models import SwarmRequest, SwarmResult
from swarm.exceptions import SwarmError

logger = logging.getLogger(__name__)


class SwarmPersistence:
    """
    Persistence engine saving swarm requests, results, agent executions, and evaluation references.
    """

    def __init__(self, base_dir: Path = Path("outputs/swarms")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_swarm_result(self, request: SwarmRequest, result: SwarmResult) -> Path:
        """
        Persists a SwarmResult and SwarmRequest under outputs/swarms/swarm=<uuid>/swarm_manifest.json.
        
        Args:
            request (SwarmRequest): Request configuration.
            result (SwarmResult): Campaign result.
            
        Returns:
            Path: Path to created manifest JSON file.
        """
        try:
            swarm_dir = self.base_dir / f"swarm={result.swarm_id}"
            swarm_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = swarm_dir / "swarm_manifest.json"

            payload = {
                "request": json.loads(request.model_dump_json()),
                "result": json.loads(result.model_dump_json())
            }

            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            logger.info(f"Persisted swarm manifest for swarm_id={result.swarm_id} at {manifest_path}")
            return manifest_path

        except Exception as e:
            raise SwarmError(f"Failed to persist swarm manifest: {e}", swarm_id=str(result.swarm_id)) from e

    def load_swarm_result(self, swarm_id: UUID) -> Dict[str, Any]:
        """
        Loads an existing swarm manifest by swarm UUID.
        """
        manifest_path = self.base_dir / f"swarm={swarm_id}" / "swarm_manifest.json"
        if not manifest_path.exists():
            raise SwarmError(f"Swarm manifest not found at {manifest_path}", swarm_id=str(swarm_id))

        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_all_swarms(self) -> List[Dict[str, Any]]:
        """
        Lists all persisted swarm manifests across outputs/swarms/.
        """
        swarms: List[Dict[str, Any]] = []
        for manifest_path in self.base_dir.glob("swarm=*/swarm_manifest.json"):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    swarms.append(json.load(f))
            except Exception as err:
                logger.warning(f"Error reading swarm manifest {manifest_path}: {err}")

        return swarms
