"""
CampaignPersistence manager for atomic JSON disk operations under campaigns/.
"""

import json
import logging
from pathlib import Path
from uuid import UUID
from typing import Dict, Any, List, Optional

from campaign.models import CampaignConfig, CampaignMetrics, CampaignBudget, CampaignResult
from campaign.exceptions import CampaignError

logger = logging.getLogger(__name__)


class CampaignPersistence:
    """
    Persistence layer performing atomic writes for manifest, queue, workers,
    metrics, budget, results, and checkpoint files.
    """

    def __init__(self, base_dir: Path = Path("campaigns")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _atomic_write_json(self, target_path: Path, data: Any) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = target_path.with_suffix(".json.tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp_path.replace(target_path)

    def save_campaign_manifest(self, config: CampaignConfig) -> Path:
        """Saves manifest.json for a campaign."""
        path = self.base_dir / f"campaign={config.campaign_id}" / "manifest.json"
        self._atomic_write_json(path, json.loads(config.model_dump_json()))
        return path

    def save_queue(self, campaign_id: UUID, queue: List[Dict[str, Any]]) -> Path:
        """Saves queue.json for a campaign."""
        path = self.base_dir / f"campaign={campaign_id}" / "queue.json"
        self._atomic_write_json(path, queue)
        return path

    def save_workers(self, campaign_id: UUID, workers: List[Dict[str, Any]]) -> Path:
        """Saves workers.json for a campaign."""
        path = self.base_dir / f"campaign={campaign_id}" / "workers.json"
        self._atomic_write_json(path, workers)
        return path

    def save_metrics(self, campaign_id: UUID, metrics: CampaignMetrics) -> Path:
        """Saves metrics.json for a campaign."""
        path = self.base_dir / f"campaign={campaign_id}" / "metrics.json"
        self._atomic_write_json(path, json.loads(metrics.model_dump_json()))
        return path

    def save_budget(self, campaign_id: UUID, budget: CampaignBudget) -> Path:
        """Saves budget.json for a campaign."""
        path = self.base_dir / f"campaign={campaign_id}" / "budget.json"
        self._atomic_write_json(path, json.loads(budget.model_dump_json()))
        return path

    def save_results(self, campaign_id: UUID, results: Dict[str, Any]) -> Path:
        """Saves results.json for a campaign."""
        path = self.base_dir / f"campaign={campaign_id}" / "results.json"
        self._atomic_write_json(path, results)
        return path

    def load_campaign_manifest(self, campaign_id: UUID) -> CampaignConfig:
        """Loads manifest.json for a campaign."""
        path = self.base_dir / f"campaign={campaign_id}" / "manifest.json"
        if not path.exists():
            raise CampaignError(f"Manifest not found for campaign '{campaign_id}'", campaign_id=str(campaign_id))
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CampaignConfig.model_validate(data)

    def list_all_campaigns(self) -> List[Dict[str, Any]]:
        """Lists all campaigns across campaigns/."""
        campaigns: List[Dict[str, Any]] = []
        for manifest_path in self.base_dir.glob("campaign=*/manifest.json"):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    campaigns.append(json.load(f))
            except Exception as err:
                logger.warning(f"Error loading campaign manifest {manifest_path}: {err}")
        return campaigns
