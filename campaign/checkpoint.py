"""
CampaignCheckpointManager for saving, loading, and pruning campaign checkpoints.
"""

import json
import logging
from pathlib import Path
from uuid import UUID
from typing import List, Dict, Any, Optional

from campaign.models import CampaignCheckpoint, CampaignBudget, CampaignStatus
from campaign.exceptions import CheckpointError

logger = logging.getLogger(__name__)


class CampaignCheckpointManager:
    """
    Manager handling checkpoint creation, atomic disk writing, loading, and pruning
    to guarantee crash-recovery for distributed campaigns.
    """

    def __init__(self, base_dir: Path = Path("campaigns")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, checkpoint: CampaignCheckpoint) -> Path:
        """
        Atomically persists a CampaignCheckpoint to campaigns/<uuid>/checkpoint.json.
        """
        try:
            campaign_dir = self.base_dir / f"campaign={checkpoint.campaign_id}"
            campaign_dir.mkdir(parents=True, exist_ok=True)

            target_path = campaign_dir / "checkpoint.json"
            tmp_path = campaign_dir / "checkpoint.json.tmp"

            payload = json.loads(checkpoint.model_dump_json())

            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)

            tmp_path.replace(target_path)
            logger.info(f"Saved campaign checkpoint for {checkpoint.campaign_id} at {target_path}")
            return target_path

        except Exception as e:
            raise CheckpointError(str(checkpoint.campaign_id), f"Failed to save checkpoint: {e}") from e

    def load_checkpoint(self, campaign_id: UUID) -> CampaignCheckpoint:
        """
        Loads a CampaignCheckpoint model from disk by campaign UUID.
        """
        target_path = self.base_dir / f"campaign={campaign_id}" / "checkpoint.json"
        if not target_path.exists():
            raise CheckpointError(str(campaign_id), f"Checkpoint file not found at {target_path}")

        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CampaignCheckpoint.model_validate(data)
        except Exception as e:
            raise CheckpointError(str(campaign_id), f"Failed to parse checkpoint: {e}") from e

    def prune_old_checkpoints(self, campaign_id: UUID, keep: int = 3) -> None:
        """
        Prunes old checkpoint backup files if present.
        """
        campaign_dir = self.base_dir / f"campaign={campaign_id}"
        if not campaign_dir.exists():
            return
        
        backups = sorted(list(campaign_dir.glob("checkpoint_*.json")))
        if len(backups) > keep:
            for old_file in backups[:-keep]:
                old_file.unlink(missing_ok=True)
