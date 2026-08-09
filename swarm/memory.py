"""
Thread-Safe Shared Memory Store for AegisSwarm Swarm Agents.
"""

import copy
import threading
import logging
from typing import Dict, Any, Optional
from swarm.exceptions import SharedMemoryError

logger = logging.getLogger(__name__)


class SwarmMemory:
    """
    Thread-safe shared memory repository storing state across agent executions.
    Stores completed attacks, failed attacks, discovered leakage, evaluator findings,
    conversation history, strategy history, prefixes/suffixes, failure reasons, and evaluation summaries.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._init_store()

    def _init_store(self) -> None:
        self._store: Dict[str, Any] = {
            "completed_attacks": [],
            "failed_attacks": [],
            "discovered_leakage": [],
            "evaluator_findings": [],
            "conversation_history": [],
            "strategy_history": [],
            "successful_prefixes": [],
            "successful_suffixes": [],
            "failure_reasons": [],
            "evaluation_summaries": [],
            "metadata": {}
        }

    def put(self, key: str, value: Any) -> None:
        """
        Puts a value into shared memory associated with a key.
        """
        with self._lock:
            self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a value from shared memory.
        """
        with self._lock:
            return self._store.get(key, default)

    def append_to_list(self, key: str, item: Any) -> None:
        """
        Appends an item to a list stored under the given key.
        """
        with self._lock:
            if key not in self._store:
                self._store[key] = []
            if not isinstance(self._store[key], list):
                raise SharedMemoryError(key, f"Stored value for '{key}' is not a list.")
            self._store[key].append(item)

    def exists(self, key: str) -> bool:
        """
        Checks if a key exists in shared memory.
        """
        with self._lock:
            return key in self._store

    def remove(self, key: str) -> None:
        """
        Removes a key from shared memory if present.
        """
        with self._lock:
            if key in self._store:
                del self._store[key]

    def clear(self) -> None:
        """
        Clears and reinitializes shared memory state.
        """
        with self._lock:
            self._init_store()

    def snapshot(self) -> Dict[str, Any]:
        """
        Returns a deep copy immutable snapshot of shared memory data.
        """
        with self._lock:
            return copy.deepcopy(self._store)
