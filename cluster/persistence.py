"""
ClusterPersistence module for atomic state persistence to outputs/cluster/.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from cluster.models import WorkerNode, ClusterStateModel, ClusterTask
from cluster.exceptions import ClusterError

logger = logging.getLogger(__name__)


class ClusterPersistence:
    """
    Persistence engine saving workers.json, cluster_state.json, scheduler_state.json, and executions.jsonl.
    """

    def __init__(self, base_dir: Path = Path("outputs/cluster")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_workers(self, workers: List[WorkerNode]) -> Path:
        """Atomically saves workers.json."""
        target = self.base_dir / "workers.json"
        tmp = self.base_dir / "workers.json.tmp"
        data = [w.model_dump(mode="json") for w in workers]
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp.replace(target)
        return target

    def save_cluster_state(self, state: ClusterStateModel) -> Path:
        """Atomically saves cluster_state.json."""
        target = self.base_dir / "cluster_state.json"
        tmp = self.base_dir / "cluster_state.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state.model_dump(mode="json"), f, indent=2)
        tmp.replace(target)
        return target

    def save_scheduler_state(self, tasks: List[ClusterTask]) -> Path:
        """Atomically saves scheduler_state.json."""
        target = self.base_dir / "scheduler_state.json"
        tmp = self.base_dir / "scheduler_state.json.tmp"
        data = [t.model_dump(mode="json") for t in tasks]
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp.replace(target)
        return target

    def log_execution(self, record: Dict[str, Any]) -> Path:
        """Appends execution log entry to executions.jsonl."""
        target = self.base_dir / "executions.jsonl"
        with open(target, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return target
