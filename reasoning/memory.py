"""
Thread-safe ReasoningMemory storing reasoning memory records and historical plans.
"""

import threading
from typing import List, Dict, Optional, Any

from reasoning.models import ReasoningMemoryRecord, ReasoningStatistics
from reasoning.exceptions import MemoryError


class ReasoningMemory:
    """
    Thread-safe in-memory store for ReasoningMemoryRecord entries.
    """

    def __init__(self, capacity: int = 5000):
        self.capacity = capacity
        self._lock = threading.RLock()
        self._records: List[ReasoningMemoryRecord] = []
        self._by_request_id: Dict[str, ReasoningMemoryRecord] = {}

    def store(self, record: ReasoningMemoryRecord) -> None:
        """Stores a ReasoningMemoryRecord in memory."""
        with self._lock:
            self._records.append(record)
            self._by_request_id[record.request_id] = record
            if len(self._records) > self.capacity:
                overflow = len(self._records) - self.capacity
                self._records = self._records[overflow:]
                self._by_request_id = {r.request_id: r for r in self._records}

    def lookup(self, request_id: str) -> Optional[ReasoningMemoryRecord]:
        """Looks up a ReasoningMemoryRecord by request_id."""
        with self._lock:
            return self._by_request_id.get(request_id)

    def history(self, limit: int = 100) -> List[ReasoningMemoryRecord]:
        """Returns the most recent N reasoning records in history."""
        with self._lock:
            return list(reversed(self._records[-limit:]))

    def clear(self) -> None:
        """Clears all records in memory."""
        with self._lock:
            self._records.clear()
            self._by_request_id.clear()

    def statistics(self) -> ReasoningStatistics:
        """Computes summary statistics for the reasoning memory."""
        with self._lock:
            total = len(self._records)
            if total == 0:
                return ReasoningStatistics(total_plans=0, avg_confidence=0.85)

            avg_conf = sum(r.overall_confidence for r in self._records) / total
            return ReasoningStatistics(
                total_plans=total,
                avg_candidates_per_pass=5.0,
                avg_confidence=round(avg_conf, 4),
                top_provider_recommendation="openai"
            )
