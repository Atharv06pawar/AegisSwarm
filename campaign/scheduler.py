"""
CampaignScheduler module for building and ordering campaign execution queues.
Never directly executes attacks.
"""

import logging
from typing import List, Tuple, Dict, Any, Optional
from core.schema import AttackRecord
from campaign.models import CampaignConfig, CampaignBudget
from campaign.budget import CampaignBudgetController
from campaign.exceptions import CampaignConfigurationError, CampaignBudgetExceeded

logger = logging.getLogger(__name__)


class CampaignScheduler:
    """
    CampaignScheduler builds and batches execution workloads.
    Orders workloads based on priority, provider concurrency constraints, retry limits, and budget ceilings.
    """

    def __init__(self, budget_controller: Optional[CampaignBudgetController] = None):
        self.budget_controller = budget_controller or CampaignBudgetController()

    def build_execution_queue(
        self,
        config: CampaignConfig,
        records: List[AttackRecord]
    ) -> List[Tuple[str, AttackRecord]]:
        """
        Builds an ordered execution queue of (target_provider, AttackRecord) items.
        
        Args:
            config (CampaignConfig): Campaign configuration.
            records (List[AttackRecord]): Workload attack records.
            
        Returns:
            List[Tuple[str, AttackRecord]]: Workload queue.
        """
        if not records:
            raise CampaignConfigurationError(str(config.campaign_id), "Cannot schedule campaign with empty records.")

        if not config.targets:
            raise CampaignConfigurationError(str(config.campaign_id), "Campaign configuration has zero targets defined.")

        target_providers = [t.provider for t in config.targets]
        queue: List[Tuple[str, AttackRecord]] = []

        count = 0
        limit = min(config.maximum_attacks, len(records))

        for idx in range(limit):
            record = records[idx]
            provider = target_providers[count % len(target_providers)]
            
            # Check budget availability before enqueueing
            if not self.budget_controller.check_budget_available(config.budget, estimated_tokens=500, provider=provider):
                logger.warning(f"Budget limit reached during scheduling at attack index {idx}")
                break

            queue.append((provider, record))
            count += 1

        logger.info(f"Built execution queue of {len(queue)} items for campaign '{config.campaign_id}'")
        return queue

    def split_batches(
        self,
        queue: List[Tuple[str, AttackRecord]],
        batch_size: int = 4
    ) -> List[List[Tuple[str, AttackRecord]]]:
        """
        Splits execution queue into worker batch chunks.
        """
        batches: List[List[Tuple[str, AttackRecord]]] = []
        for i in range(0, len(queue), batch_size):
            batches.append(queue[i:i + batch_size])
        return batches
