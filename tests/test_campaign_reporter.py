import pytest
import json
from campaign.models import CampaignConfig, CampaignObjective, CampaignMetrics
from campaign.reporter import CampaignReportGenerator


def test_report_generator_markdown():
    """Verify Markdown report formatting."""
    config = CampaignConfig(name="Report Test", objective=CampaignObjective(name="Obj"))
    metrics = CampaignMetrics(completed_attacks=10, failed_attacks=2, average_latency=120.0)

    md = CampaignReportGenerator.generate_markdown(config, metrics)
    assert "# Campaign Audit Report: Report Test" in md
    assert "120.00 ms" in md


def test_report_generator_json_and_csv():
    """Verify JSON and CSV report formatting."""
    config = CampaignConfig(name="Report Test", objective=CampaignObjective(name="Obj"))
    metrics = CampaignMetrics(completed_attacks=10, failed_attacks=2, average_latency=120.0)

    json_str = CampaignReportGenerator.generate_json(config, metrics)
    data = json.loads(json_str)
    assert data["name"] == "Report Test"

    csv_str = CampaignReportGenerator.generate_csv(config, metrics)
    assert "campaign_id" in csv_str
    assert "completed_attacks,10" in csv_str
