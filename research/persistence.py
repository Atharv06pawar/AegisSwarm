"""
Persistence handler for AegisSwarm Research Subsystem benchmark reports.
"""

import json
import os
from typing import Optional, List
from research.models import BenchmarkReport


class ResearchPersistence:
    """
    Manages loading and persisting research benchmark reports to disk.
    """

    def __init__(self, reports_dir: str = "outputs/reports"):
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

    def save_report(self, report: BenchmarkReport) -> str:
        """
        Saves a benchmark report to outputs/reports/benchmark.json.
        """
        filepath = os.path.join(self.reports_dir, "benchmark.json")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(report.model_dump(), indent=2))

        # Also save historical timestamped copy
        hist_file = os.path.join(self.reports_dir, f"benchmark_{report.benchmark_id}.json")
        with open(hist_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(report.model_dump(), indent=2))

        return filepath

    def get_latest_report(self) -> Optional[BenchmarkReport]:
        """
        Retrieves the latest saved benchmark report from outputs/reports/benchmark.json.
        """
        filepath = os.path.join(self.reports_dir, "benchmark.json")
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return BenchmarkReport(**data)
        except Exception:
            return None

    def list_reports(self) -> List[BenchmarkReport]:
        """
        Lists all saved benchmark reports for historical repeatability analysis.
        """
        reports: List[BenchmarkReport] = []
        if not os.path.exists(self.reports_dir):
            return reports

        for fname in os.listdir(self.reports_dir):
            if fname.startswith("benchmark") and fname.endswith(".json"):
                fpath = os.path.join(self.reports_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    reports.append(BenchmarkReport(**data))
                except Exception:
                    pass

        if not reports:
            latest = self.get_latest_report()
            if latest:
                reports.append(latest)

        return reports
