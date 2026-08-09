"""
CheckpointManager persisting and retrieving mission state snapshots.
"""

import json
from pathlib import Path
from typing import Optional, List
from uuid import UUID

from orchestrator.models import MissionCheckpoint, MissionState
from orchestrator.exceptions import CheckpointError


class CheckpointManager:
    """
    Manages atomic writing and loading of MissionCheckpoint snapshots under outputs/orchestrator/checkpoints/.
    """

    def __init__(self, base_dir: Path = Path("outputs/orchestrator")):
        self.base_dir = Path(base_dir)
        self.checkpoints_dir = self.base_dir / "checkpoints"
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, checkpoint: MissionCheckpoint) -> Path:
        """Atomically saves a MissionCheckpoint object to disk."""
        target = self.checkpoints_dir / f"chk_{checkpoint.mission_id}_{checkpoint.checkpoint_id}.json"
        tmp = self.checkpoints_dir / f"chk_{checkpoint.mission_id}_{checkpoint.checkpoint_id}.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(checkpoint.model_dump_json())
        tmp.replace(target)
        return target

    def get_latest_checkpoint(self, mission_id: UUID) -> Optional[MissionCheckpoint]:
        """Loads the most recent checkpoint for a given mission_id."""
        files = list(self.checkpoints_dir.glob(f"chk_{mission_id}_*.json"))
        if not files:
            return None
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        with open(files[0], "r", encoding="utf-8") as f:
            data = json.load(f)
            return MissionCheckpoint.model_validate(data)
