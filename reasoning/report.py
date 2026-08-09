"""
ReasoningReportGenerator producing structured Markdown and JSON reasoning audit reports.
"""

import json
from typing import Dict, Any
from reasoning.models import ReasoningResponse


class ReasoningReportGenerator:
    """
    Report generator producing Markdown and JSON reports from ReasoningResponse.
    """

    def generate_report(self, response: ReasoningResponse, format_type: str = "markdown") -> str:
        """
        Generates formatted Markdown or JSON audit report containing strategy, critique, reflection, provider, and confidence details.
        """
        if format_type.lower() == "json":
            return json.dumps(response.model_dump(mode="json"), indent=2)

        md_lines = [
            f"# AegisSwarm Autonomous Reasoning Report",
            f"**Request ID**: `{response.request_id}`",
            f"**Overall Confidence**: `{response.overall_confidence * 100:.1f}%`",
            "",
            "## 1. Chosen Strategy Candidate",
            f"- **Attack Family**: `{response.chosen_strategy.attack_family}`",
            f"- **Mutation Family**: `{response.chosen_strategy.mutation_family}`",
            f"- **Target Provider**: `{response.chosen_strategy.provider}:{response.chosen_strategy.model}`",
            f"- **Estimated Success**: `{response.chosen_strategy.estimated_success * 100:.1f}%`",
            f"- **Estimated Cost**: `${response.chosen_strategy.estimated_cost:.4f}`",
            f"- **Reasoning**: {response.chosen_strategy.reasoning_text}",
            "",
            "## 2. Target Provider Recommendation",
            f"- **Recommended Provider**: `{response.provider_recommendation.recommended_provider}`",
            f"- **Model**: `{response.provider_recommendation.recommended_model}`",
            f"- **Rationale**: {response.provider_recommendation.rationale}",
            "",
            "## 3. Mutation Chain Plan",
            f"- **Mutation Chain**: `{' -> '.join(response.mutation_plan.chain)}`",
            f"- **Expected Evasion Rate**: `{response.mutation_plan.expected_evasion_rate * 100:.1f}%`",
            "",
            "## 4. Candidate Generation & Self-Critique",
            f"Generated `{len(response.all_candidates)}` strategy candidates. Self-critique score evaluated across novelty, risk, cost, and complexity.",
            "",
            "## 5. Post-Execution Reflection Analysis",
        ]

        for ref in response.reflections:
            md_lines.extend([
                f"- **What Worked**: {ref.what_worked}",
                f"- **What Failed**: {ref.what_failed}",
                f"- **Why**: {ref.why_outcome}",
                f"- **Improvement Guidance**: {ref.how_to_improve}",
            ])

        return "\n".join(md_lines)
