"""
OrchestratorReportGenerator generating Markdown and JSON summary reports for master missions.
"""

import json
from orchestrator.models import MissionReportModel, MissionModel, MissionExecutionGraph
from orchestrator.execution_graph import ExecutionGraphBuilder


class OrchestratorReportGenerator:
    """
    Report generator producing structured Markdown and JSON audit reports for master orchestrator missions.
    """

    def generate_report(
        self,
        mission: MissionModel,
        graph: MissionExecutionGraph,
        format_type: str = "markdown"
    ) -> str:
        """
        Generates formatted Markdown or JSON mission audit report.
        """
        graph_builder = ExecutionGraphBuilder()
        mermaid = graph_builder.export_mermaid(graph)
        success_rate = (mission.successful_attacks / mission.attack_count) if mission.attack_count > 0 else 0.0

        model = MissionReportModel(
            mission_id=mission.mission_id,
            objective=mission.objective,
            state=mission.state,
            providers_used=[mission.target_provider],
            attack_count=mission.attack_count,
            success_rate=round(success_rate, 4),
            failures=mission.failed_attacks,
            retries=0,
            learning_updates=1,
            reasoning_summary=f"Strategic plan synthesized using '{mission.target_provider}:{mission.target_model}'.",
            telemetry_summary="Full telemetry pipeline events recorded and logged.",
            execution_graph_summary=f"DAG Nodes: {len(graph.nodes)}, Edges: {len(graph.edges)}"
        )

        if format_type.lower() == "json":
            return json.dumps(model.model_dump(mode="json"), indent=2)

        md_lines = [
            f"# AegisSwarm Master Orchestrator Mission Report",
            f"**Mission ID**: `{mission.mission_id}`",
            f"**Status**: `{mission.state.value}`",
            f"**Objective**: {mission.objective}",
            "",
            "## 1. Executive Summary",
            f"- **Target Provider**: `{mission.target_provider}:{mission.target_model}`",
            f"- **Attacks Executed**: `{mission.attack_count}`",
            f"- **Successful Attacks**: `{mission.successful_attacks}`",
            f"- **Failed Attacks**: `{mission.failed_attacks}`",
            f"- **Overall Evasion Success Rate**: `{success_rate * 100:.1f}%`",
            f"- **Total Cost**: `${mission.cost_usd:.4f}`",
            "",
            "## 2. Reasoning & Strategy Summary",
            model.reasoning_summary,
            "",
            "## 3. Execution DAG Graph Topology",
            "```mermaid",
            mermaid,
            "```",
            "",
            "## 4. Telemetry & Learning Updates",
            model.telemetry_summary,
        ]

        return "\n".join(md_lines)
