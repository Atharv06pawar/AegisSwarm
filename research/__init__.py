"""
AegisSwarm Research Validation & Production End-to-End Benchmark Harness Subsystem.
"""

from research.models import (
    BenchmarkRequest,
    BenchmarkReport,
    DatasetBenchmarkMetric,
    ProviderBenchmarkMetric,
    StrategyBenchmarkMetric,
    SwarmAgentBenchmarkMetric,
    LearningBenchmarkMetric,
    TelemetryBenchmarkMetric,
)
from research.harness import ResearchBenchmarkHarness
from research.reports import ResearchReportGenerator

__all__ = [
    "BenchmarkRequest",
    "BenchmarkReport",
    "DatasetBenchmarkMetric",
    "ProviderBenchmarkMetric",
    "StrategyBenchmarkMetric",
    "SwarmAgentBenchmarkMetric",
    "LearningBenchmarkMetric",
    "TelemetryBenchmarkMetric",
    "ResearchBenchmarkHarness",
    "ResearchReportGenerator",
]
