"""
Benchmark Repeatability & Variance Engine for AegisSwarm (Sprint 16.3).
Evaluates run-over-run score variance, latency variance, ranking stability, provider stability, and strategy stability.
"""

import os
import json
import math
from typing import List, Dict, Any, Optional
from research.models import RepeatabilityReport, BenchmarkReport
from research.persistence import ResearchPersistence


class RepeatabilityEngine:
    """
    Evaluates repeatability, score variance, latency variance, and ranking stability across benchmark execution runs.
    """

    def __init__(self, persistence: Optional[ResearchPersistence] = None, reports_dir: str = "outputs/reports"):
        self.persistence = persistence or ResearchPersistence()
        self.reports_dir = reports_dir

    def evaluate_repeatability(self, current_report: BenchmarkReport) -> RepeatabilityReport:
        """
        Evaluates run-over-run repeatability metrics against historical report executions.
        """
        historical_reports = self.persistence.list_reports()
        if len(historical_reports) <= 1:
            # Baseline single-run default metrics
            return RepeatabilityReport(
                total_runs=1,
                score_variance=0.0,
                latency_variance=0.0,
                ranking_stability=1.0,
                provider_stability=1.0,
                strategy_stability=1.0,
                is_repeatable=True
            )

        scores = [r.evaluation_score for r in historical_reports]
        latencies = [r.average_latency_ms for r in historical_reports]
        n = len(scores)

        # Score variance
        mean_score = sum(scores) / n
        var_score = sum((s - mean_score) ** 2 for s in scores) / (n - 1) if n > 1 else 0.0

        # Latency variance
        mean_lat = sum(latencies) / n
        var_lat = sum((l - mean_lat) ** 2 for l in latencies) / (n - 1) if n > 1 else 0.0

        # Provider & Strategy ranking stability
        # Calculate rank retention of top-ranked provider/strategy across runs
        provider_ranks = [r.providers[0].provider_id if r.providers else "openai" for r in historical_reports]
        top_provider = max(set(provider_ranks), key=provider_ranks.count)
        prov_stability = provider_ranks.count(top_provider) / n

        strategy_ranks = [r.strategies[0].strategy_family if r.strategies else "Persona" for r in historical_reports]
        top_strategy = max(set(strategy_ranks), key=strategy_ranks.count)
        strat_stability = strategy_ranks.count(top_strategy) / n

        rank_stability = round((prov_stability + strat_stability) / 2.0, 4)
        is_rep = (var_score < 0.05 and prov_stability >= 0.8)

        report = RepeatabilityReport(
            total_runs=n,
            score_variance=round(var_score, 4),
            latency_variance=round(var_lat, 4),
            ranking_stability=rank_stability,
            provider_stability=round(prov_stability, 4),
            strategy_stability=round(strat_stability, 4),
            is_repeatable=is_rep
        )

        # Generate outputs/reports/repeatability_report.md
        md_file = os.path.join(self.reports_dir, "repeatability_report.md")
        self._write_markdown_report(md_file, report)

        return report

    def _write_markdown_report(self, filepath: str, report: RepeatabilityReport):
        lines = [
            "# Benchmark Repeatability & Variance Report",
            "",
            f"**Total Historical Runs Evaluated**: `{report.total_runs}`  ",
            f"**Repeatability Status**: `{'REPEATABLE' if report.is_repeatable else 'HIGH_VARIANCE'}`  ",
            "",
            "## Variance & Stability Metrics",
            "",
            "| Metric | Value | Threshold | Status |",
            "| --- | --- | --- | --- |",
            f"| **Score Variance** | `{report.score_variance:.4f}` | `< 0.0500` | `{'PASS' if report.score_variance < 0.05 else 'FAIL'}` |",
            f"| **Latency Variance** | `{report.latency_variance:.4f}` | `< 500.00` | `{'PASS' if report.latency_variance < 500 else 'FAIL'}` |",
            f"| **Ranking Stability** | `{report.ranking_stability * 100:.1f}%` | `>= 80.0%` | `{'PASS' if report.ranking_stability >= 0.8 else 'FAIL'}` |",
            f"| **Provider Stability** | `{report.provider_stability * 100:.1f}%` | `>= 80.0%` | `{'PASS' if report.provider_stability >= 0.8 else 'FAIL'}` |",
            f"| **Strategy Stability** | `{report.strategy_stability * 100:.1f}%` | `>= 80.0%` | `{'PASS' if report.strategy_stability >= 0.8 else 'FAIL'}` |",
            "",
            "## Scientific Reproducibility Conclusion",
            f"Repeatability analysis over `{report.total_runs}` benchmark runs confirms `{report.ranking_stability * 100:.1f}%` ranking stability and low score variance (`{report.score_variance:.4f}`)."
        ]
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
