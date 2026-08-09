"""
OrchestratorPersistence managing directories and atomic disk file writing under outputs/orchestrator/.
"""

import json
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from orchestrator.models import MissionModel, MissionExecutionGraph
from orchestrator.exceptions import OrchestratorError


class OrchestratorPersistence:
    """
    Persistence manager for saving missions, execution graphs, checkpoints, and reports.
    """

    def __init__(self, base_dir: Path = Path("outputs/orchestrator")):
        self.base_dir = Path(base_dir)
        self.missions_dir = self.base_dir / "missions"
        self.checkpoints_dir = self.base_dir / "checkpoints"
        self.graphs_dir = self.base_dir / "graphs"
        self.reports_dir = self.base_dir / "reports"

        for d in [self.missions_dir, self.checkpoints_dir, self.graphs_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def save_mission(self, mission: MissionModel) -> Path:
        """Atomically saves mission manifest file."""
        target = self.missions_dir / f"mission_{mission.mission_id}.json"
        tmp = self.missions_dir / f"mission_{mission.mission_id}.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(mission.model_dump_json())
        tmp.replace(target)
        return target

    def save_graph(self, graph: MissionExecutionGraph) -> Path:
        """Atomically saves execution graph topology."""
        target = self.graphs_dir / f"graph_{graph.mission_id}.json"
        tmp = self.graphs_dir / f"graph_{graph.mission_id}.json.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(graph.model_dump_json())
        tmp.replace(target)
        return target

    def save_report(self, mission_id: UUID, report_content: str, extension: str = "md") -> Path:
        """Saves mission report to disk."""
        target = self.reports_dir / f"mission_report_{mission_id}.{extension}"
        with open(target, "w", encoding="utf-8") as f:
            f.write(report_content)
        return target
