"""
RetryPolicy manager for tracking attack retries and computing exponential backoffs.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class RetryPolicy:
    """
    Production retry policy managing retry eligibility, exponential backoffs, and historical attempt logs.
    """

    def __init__(self, max_attempts: int = 3, backoff_factor: float = 2.0, initial_backoff_sec: float = 1.0):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
        self.initial_backoff_sec = initial_backoff_sec
        self._retry_history: Dict[str, List[Dict[str, Any]]] = {}

    def is_eligible_for_retry(
        self,
        attack_id: str,
        attempt_count: int,
        refusal_detected: bool = False,
        max_attempts_override: Optional[int] = None
    ) -> bool:
        """
        Determines whether an attack attempt is eligible for retry.
        
        Args:
            attack_id (str): Attack record sample_id.
            attempt_count (int): Current attempt number (1-indexed).
            refusal_detected (bool): Whether the model explicitly refused.
            max_attempts_override (Optional[int]): Optional max attempts override.
            
        Returns:
            bool: True if retry is eligible, False otherwise.
        """
        limit = max_attempts_override or self.max_attempts
        if attempt_count >= limit:
            return False

        # If a hard refusal was detected, retrying without payload mutation is futile
        if refusal_detected:
            return False

        return True

    def get_next_backoff_sec(self, attempt_count: int) -> float:
        """
        Computes exponential backoff delay in seconds for the given attempt count.
        
        Formula: initial_backoff_sec * (backoff_factor ^ (attempt_count - 1))
        """
        if attempt_count <= 0:
            return 0.0
        return round(self.initial_backoff_sec * (self.backoff_factor ** (attempt_count - 1)), 2)

    def record_attempt(self, attack_id: str, attempt_num: int, success: bool, reason: str = "") -> None:
        """
        Records a retry attempt in history.
        """
        if attack_id not in self._retry_history:
            self._retry_history[attack_id] = []

        self._retry_history[attack_id].append({
            "attempt": attempt_num,
            "success": success,
            "reason": reason,
            "backoff_sec": self.get_next_backoff_sec(attempt_num)
        })

    def get_retry_history(self, attack_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves retry history for a specific attack ID.
        """
        return self._retry_history.get(attack_id, [])
