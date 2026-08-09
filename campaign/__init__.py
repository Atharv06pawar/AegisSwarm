"""
AegisSwarm Distributed Campaign Engine package.
"""

from campaign.models import (
    CampaignConfig,
    CampaignObjective,
    CampaignTarget,
    CampaignBudget,
    CampaignStatus,
    CampaignWorker,
    CampaignProgress,
    CampaignEvent,
    CampaignMetrics,
    CampaignCheckpoint,
    CampaignResult,
    CampaignSummary
)
from campaign.exceptions import (
    CampaignError,
    CampaignConfigurationError,
    CampaignNotFound,
    CampaignBudgetExceeded,
    CampaignStateError,
    WorkerError,
    CheckpointError
)
from campaign.manager import CampaignManager
from campaign.scheduler import CampaignScheduler
from campaign.worker import CampaignWorkerPool
from campaign.dispatcher import CampaignDispatcher
from campaign.budget import CampaignBudgetController
from campaign.checkpoint import CampaignCheckpointManager
from campaign.persistence import CampaignPersistence
from campaign.metrics import CampaignMetricsCollector
from campaign.reporter import CampaignReportGenerator

__all__ = [
    "CampaignManager",
    "CampaignScheduler",
    "CampaignWorkerPool",
    "CampaignDispatcher",
    "CampaignBudgetController",
    "CampaignCheckpointManager",
    "CampaignPersistence",
    "CampaignMetricsCollector",
    "CampaignReportGenerator",
    "CampaignConfig",
    "CampaignObjective",
    "CampaignTarget",
    "CampaignBudget",
    "CampaignStatus",
    "CampaignWorker",
    "CampaignProgress",
    "CampaignEvent",
    "CampaignMetrics",
    "CampaignCheckpoint",
    "CampaignResult",
    "CampaignSummary",
    "CampaignError",
    "CampaignConfigurationError",
    "CampaignNotFound",
    "CampaignBudgetExceeded",
    "CampaignStateError",
    "WorkerError",
    "CheckpointError"
]
