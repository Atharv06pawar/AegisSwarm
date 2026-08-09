"""
EvaluationReportGenerator module for exporting Markdown and JSON evaluation reports.
"""

import json
from typing import List, Dict, Any
from evaluation.models import EvaluationResult, EvaluationSummary


class EvaluationReportGenerator:
    """
    Reporting utility exporting evaluation summaries and detailed breakdowns in Markdown and JSON formats.
    """

    @staticmethod
    def generate_json_report(summary: EvaluationSummary, results: List[EvaluationResult]) -> str:
        """
        Generates a structured JSON string report.
        """
        detector_counts: Dict[str, int] = {}
        for res in results:
            for d in res.detectors_used:
                detector_counts[d] = detector_counts.get(d, 0) + 1

        payload = {
            "summary": json.loads(summary.model_dump_json()),
            "detector_breakdown": detector_counts,
            "results_count": len(results),
            "recommendations": [
                "Enforce system prompt isolation for detected prompt leakage vectors.",
                "Harden refusal filtering for boundary condition jailbreak prompts.",
                "Review high severity score (>8.0) evaluation results."
            ],
            "results": [json.loads(r.model_dump_json()) for r in results]
        }
        return json.dumps(payload, indent=2)

    @staticmethod
    def generate_markdown_report(summary: EvaluationSummary, results: List[EvaluationResult]) -> str:
        """
        Generates a formatted GitHub-flavored Markdown evaluation report.
        """
        detector_counts: Dict[str, int] = {}
        for res in results:
            for d in res.detectors_used:
                detector_counts[d] = detector_counts.get(d, 0) + 1

        md_lines = [
            "# AegisSwarm Evaluation Audit Report",
            "",
            "## Summary Metrics",
            f"- **Total Executions Evaluated**: {summary.total_evaluated}",
            f"- **Attack Success Rate**: {summary.success_rate * 100:.1f}%",
            f"- **Model Refusal Rate**: {summary.refusal_rate * 100:.1f}%",
            f"- **Prompt Leakage Rate**: {summary.leakage_rate * 100:.1f}%",
            f"- **Jailbreak Rate**: {summary.jailbreak_rate * 100:.1f}%",
            f"- **Average Severity Score**: {summary.average_severity} / 10.0",
            f"- **Average Evaluator Confidence**: {summary.average_confidence * 100:.1f}%",
            f"- **Cumulative Evaluation Latency**: {summary.total_latency_ms:.2f} ms",
            "",
            "## Detector Breakdown",
        ]

        for detector_name, count in detector_counts.items():
            md_lines.append(f"- `{detector_name}`: {count} evaluations")

        md_lines.extend([
            "",
            "## Security Recommendations",
            "1. Enforce system prompt isolation for detected prompt leakage vectors.",
            "2. Harden refusal filtering for boundary condition jailbreak prompts.",
            "3. Audit high-severity evaluation results with severity score > 8.0.",
            ""
        ])

        return "\n".join(md_lines)
