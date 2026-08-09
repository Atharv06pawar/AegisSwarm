"""
LearningPersistence module for atomic persistence of memory, graphs, strategies, scores, and optimizer state to outputs/learning/.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from learning.models import LearningMemoryRecord, AttackGraphModel
from learning.exceptions import LearningError

logger = logging.getLogger(__name__)


class LearningPersistence:
    """
    Persistence manager for atomic saving and loading of outputs/learning/ artifacts.
    """

    def __init__(self, base_dir: Path = Path("outputs/learning")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_memory(self, records: List[LearningMemoryRecord]) -> Path:
        """Atomically saves memory.jsonl."""
        target = self.base_dir / "memory.jsonl"
        tmp = self.base_dir / "memory.jsonl.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for r in records:
                f.write(r.model_dump_json() + "\n")
        tmp.replace(target)
        return target

    def save_attack_graph(self, graph_model: AttackGraphModel) -> Path:
        """Atomically saves attack_graph.json."""
        target = self.base_dir / "attack_graph.json"
        tmp = self.base_dir / "attack_graph.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(graph_model.model_dump(mode="json"), f, indent=2)
        tmp.replace(target)
        return target

    def save_strategies(self, strategies: List[Dict[str, Any]]) -> Path:
        """Atomically saves strategies.json."""
        target = self.base_dir / "strategies.json"
        tmp = self.base_dir / "strategies.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(strategies, f, indent=2)
        tmp.replace(target)
        return target

    def save_scores(self, scores: Dict[str, Any]) -> Path:
        """Atomically saves scores.json."""
        target = self.base_dir / "scores.json"
        tmp = self.base_dir / "scores.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
        tmp.replace(target)
        return target

    def save_optimizer_state(self, state: Dict[str, Any]) -> Path:
        """Atomically saves optimizer_state.json."""
        target = self.base_dir / "optimizer_state.json"
        tmp = self.base_dir / "optimizer_state.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        tmp.replace(target)
        return target
