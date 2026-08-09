"""
Thread-safe LearningMemory module storing historical execution records for adaptive learning.
"""

import threading
from uuid import UUID
from typing import List, Dict, Optional, Any

from learning.models import LearningMemoryRecord
from learning.exceptions import MemoryError


class LearningMemory:
    """
    Thread-safe in-memory and persistent store of historical attack execution outcomes.
    """

    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self._lock = threading.RLock()
        self._records: List[LearningMemoryRecord] = []
        self._by_attack_id: Dict[str, LearningMemoryRecord] = {}

    def store(self, record: LearningMemoryRecord) -> None:
        """Stores a historical execution record in memory."""
        with self._lock:
            self._records.append(record)
            self._by_attack_id[record.attack_id] = record
            if len(self._records) > self.capacity:
                self.prune(self.capacity)

    def lookup(self, attack_id: str) -> Optional[LearningMemoryRecord]:
        """Retrieves a historical memory record by attack_id."""
        with self._lock:
            return self._by_attack_id.get(attack_id)

    def history(self, limit: int = 100) -> List[LearningMemoryRecord]:
        """Returns the most recent N execution records in history."""
        with self._lock:
            return list(reversed(self._records[-limit:]))

    def forget(self, record_id: UUID) -> None:
        """Removes a specific record from memory by record_id."""
        with self._lock:
            self._records = [r for r in self._records if r.record_id != record_id]
            self._by_attack_id = {r.attack_id: r for r in self._records}

    def prune(self, max_capacity: int) -> None:
        """Prunes oldest memory records to maintain capacity limit."""
        with self._lock:
            if len(self._records) > max_capacity:
                overflow = len(self._records) - max_capacity
                self._records = self._records[overflow:]
                self._by_attack_id = {r.attack_id: r for r in self._records}

    def statistics(self) -> Dict[str, Any]:
        """Computes summary statistics over historical executions."""
        with self._lock:
            total = len(self._records)
            if total == 0:
                return {
                    "total_records": 0,
                    "overall_success_rate": 0.0,
                    "average_score": 0.0,
                    "top_mutations": {},
                    "top_agents": {}
                }

            successful = sum(1 for r in self._records if r.attack_success)
            avg_score = sum(r.evaluation_score for r in self._records) / total

            mut_counts: Dict[str, int] = {}
            agent_counts: Dict[str, int] = {}
            for r in self._records:
                mut_counts[r.mutation] = mut_counts.get(r.mutation, 0) + (1 if r.attack_success else 0)
                agent_counts[r.agent] = agent_counts.get(r.agent, 0) + (1 if r.attack_success else 0)

            return {
                "total_records": total,
                "overall_success_rate": round(successful / total, 4),
                "average_score": round(avg_score, 4),
                "top_mutations": mut_counts,
                "top_agents": agent_counts
            }
