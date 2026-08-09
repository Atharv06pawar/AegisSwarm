"""
SwarmScheduler for managing attack execution scheduling order.
"""

from typing import List, Tuple, Iterator
from core.schema import AttackRecord
from swarm.exceptions import SchedulerError


class SwarmScheduler:
    """
    Scheduler maintaining the execution queue for planned agent attacks.
    Supports sequential execution and defines scheduling order.
    """

    def __init__(self):
        self._queue: List[Tuple[str, AttackRecord]] = []

    def schedule(self, plan: List[Tuple[str, AttackRecord]]) -> List[Tuple[str, AttackRecord]]:
        """
        Builds and verifies the execution queue from a planned attack list.
        
        Args:
            plan (List[Tuple[str, AttackRecord]]): Input attack plan.
            
        Returns:
            List[Tuple[str, AttackRecord]]: Verified execution queue.
        """
        if not plan:
            raise SchedulerError("unknown", "Cannot schedule an empty attack plan.")

        self._queue = list(plan)
        return list(self._queue)

    def get_queue(self) -> List[Tuple[str, AttackRecord]]:
        """
        Returns the scheduled execution queue.
        """
        return list(self._queue)

    def iter_queue(self) -> Iterator[Tuple[str, AttackRecord]]:
        """
        Yields scheduled (agent_name, attack_record) items iteratively.
        """
        for item in self._queue:
            yield item
