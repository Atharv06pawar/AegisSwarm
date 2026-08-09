"""
ReasoningPersistence module for atomic persistence of strategies, reflections, reports, and memory.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from reasoning.models import StrategyCandidate, ReflectionResult, ReasoningMemoryRecord, ReasoningResponse
from reasoning.exceptions import ReasoningError

logger = logging.getLogger(__name__)


class ReasoningPersistence:
    """
    Persistence manager for saving strategies.jsonl, reflections.jsonl, reports/, and memory.jsonl.
    """

    def __init__(self, base_dir: Path = Path("outputs/reasoning")):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        (self.base_dir / "reports").mkdir(parents=True, exist_ok=True)

    def save_strategies(self, strategies: List[StrategyCandidate]) -> Path:
        """Atomically saves strategies.jsonl."""
        target = self.base_dir / "strategies.jsonl"
        tmp = self.base_dir / "strategies.jsonl.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for s in strategies:
                f.write(s.model_dump_json() + "\n")
        tmp.replace(target)
        return target

    def save_reflections(self, reflections: List[ReflectionResult]) -> Path:
        """Atomically saves reflections.jsonl."""
        target = self.base_dir / "reflections.jsonl"
        tmp = self.base_dir / "reflections.jsonl.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for r in reflections:
                f.write(r.model_dump_json() + "\n")
        tmp.replace(target)
        return target

    def save_memory(self, records: List[ReasoningMemoryRecord]) -> Path:
        """Atomically saves memory.jsonl."""
        target = self.base_dir / "memory.jsonl"
        tmp = self.base_dir / "memory.jsonl.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for rec in records:
                f.write(rec.model_dump_json() + "\n")
        tmp.replace(target)
        return target

    def save_report(self, request_id: str, report_text: str, extension: str = "md") -> Path:
        """Saves a reasoning report under outputs/reasoning/reports/."""
        reports_dir = self.base_dir / "reports"
        target = reports_dir / f"reasoning_report_{request_id}.{extension}"
        with open(target, "w", encoding="utf-8") as f:
            f.write(report_text)
        return target
