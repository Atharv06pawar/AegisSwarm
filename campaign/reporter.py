"""
CampaignReportGenerator module for exporting campaign reports in Markdown, JSON, and CSV.
"""

import json
import csv
import io
import logging
from typing import Dict, Any, List
from campaign.models import CampaignConfig, CampaignMetrics, CampaignResult, CampaignSummary

logger = logging.getLogger(__name__)


class CampaignReportGenerator:
    """
    Report generator exporting comprehensive campaign audit summaries.
    """

    @staticmethod
    def generate_markdown(config: CampaignConfig, metrics: CampaignMetrics) -> str:
        """Generates a GitHub Flavored Markdown audit report."""
        lines = [
            f"# Campaign Audit Report: {config.name}",
            f"**Campaign ID**: `{config.campaign_id}`  ",
            f"**Created**: {config.creation_timestamp}  ",
            f"**Objective**: {config.objective.name} ({config.objective.description})",
            "",
            "## Executive Summary",
            f"- **Total Attacks Planned/Executed**: {metrics.total_attacks} / {metrics.completed_attacks}",
            f"- **Failed Attacks**: {metrics.failed_attacks}",
            f"- **Tokens Consumed**: {metrics.tokens_consumed:,}",
            f"- **Total Budget Spent**: ${config.budget.current_cost_usd:.4f} / ${config.budget.max_cost_usd:.2f}",
            f"- **Attacks / Minute**: {metrics.attacks_per_minute}",
            "",
            "## Performance & Latency Telemetry",
            f"- **Average Latency**: {metrics.average_latency:.2f} ms",
            f"- **P95 Latency**: {metrics.p95_latency:.2f} ms",
            f"- **P99 Latency**: {metrics.p99_latency:.2f} ms",
            f"- **Average Cost / Attack**: ${metrics.average_cost:.6f}",
            "",
            "## Provider Usage Breakdown",
        ]

        for prov, cnt in metrics.provider_usage.items():
            lines.append(f"- **{prov.upper()}**: {cnt} executions")

        lines.extend([
            "",
            "## Adaptive Learning Telemetry",
            f"- **Retries Executed**: {metrics.retry_count}",
            f"- **Mutations Applied**: {metrics.mutation_count}",
            f"- **Evaluations Executed**: {metrics.evaluation_count}",
            f"- **Learning Gain**: {metrics.learning_gain:.4f}",
            "",
            "## Security & Remediation Recommendations",
            "> [!IMPORTANT]",
            "> Review provider endpoints exhibiting high failure or leakage rates. "
            "Implement input sanitization and boundary guardrails for prompt injection vectors."
        ])

        return "\n".join(lines)

    @staticmethod
    def generate_json(config: CampaignConfig, metrics: CampaignMetrics) -> str:
        """Generates a JSON audit report."""
        payload = {
            "campaign_id": str(config.campaign_id),
            "name": config.name,
            "config": json.loads(config.model_dump_json()),
            "metrics": json.loads(metrics.model_dump_json())
        }
        return json.dumps(payload, indent=2)

    @staticmethod
    def generate_csv(config: CampaignConfig, metrics: CampaignMetrics) -> str:
        """Generates a CSV report summarizing metrics."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["campaign_id", str(config.campaign_id)])
        writer.writerow(["name", config.name])
        writer.writerow(["completed_attacks", metrics.completed_attacks])
        writer.writerow(["failed_attacks", metrics.failed_attacks])
        writer.writerow(["average_latency_ms", metrics.average_latency])
        writer.writerow(["p95_latency_ms", metrics.p95_latency])
        writer.writerow(["p99_latency_ms", metrics.p99_latency])
        writer.writerow(["tokens_consumed", metrics.tokens_consumed])
        writer.writerow(["total_cost_usd", config.budget.current_cost_usd])
        return output.getvalue()
