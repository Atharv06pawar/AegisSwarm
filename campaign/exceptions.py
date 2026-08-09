"""
Custom exception hierarchy for the AegisSwarm Distributed Campaign Engine.
"""

class CampaignError(Exception):
    """Base exception for all campaign engine errors."""
    def __init__(self, message: str, campaign_id: str = "unknown"):
        self.message = message
        self.campaign_id = campaign_id
        super().__init__(f"[{campaign_id}] {message}")


class CampaignConfigurationError(CampaignError):
    """Raised when campaign parameters or settings are invalid."""
    def __init__(self, campaign_id: str, details: str):
        super().__init__(message=f"Configuration error: {details}", campaign_id=campaign_id)


class CampaignNotFound(CampaignError):
    """Raised when a requested campaign UUID is not found."""
    def __init__(self, campaign_id: str):
        super().__init__(message=f"Campaign '{campaign_id}' not found.", campaign_id=campaign_id)


class CampaignBudgetExceeded(CampaignError):
    """Raised when a campaign exceeds its USD cost or token budget limits."""
    def __init__(self, campaign_id: str, current_cost: float, max_budget: float):
        super().__init__(
            message=f"Budget limit exceeded: ${current_cost:.4f} > ${max_budget:.4f}",
            campaign_id=campaign_id
        )


class CampaignStateError(CampaignError):
    """Raised when an invalid campaign state transition is attempted."""
    def __init__(self, campaign_id: str, current_status: str, attempted_action: str):
        super().__init__(
            message=f"Cannot perform '{attempted_action}' when campaign is in status '{current_status}'.",
            campaign_id=campaign_id
        )


class WorkerError(CampaignError):
    """Raised when a worker node fails to execute or heartbeat."""
    def __init__(self, worker_id: str, campaign_id: str, details: str):
        super().__init__(message=f"Worker '{worker_id}' error: {details}", campaign_id=campaign_id)


class CheckpointError(CampaignError):
    """Raised when loading or saving a campaign checkpoint fails."""
    def __init__(self, campaign_id: str, details: str):
        super().__init__(message=f"Checkpoint error: {details}", campaign_id=campaign_id)
