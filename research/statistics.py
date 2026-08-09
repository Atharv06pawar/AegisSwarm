"""
Statistical Validation Engine for AegisSwarm Research Subsystem (Sprint 16.3).
Computes mean, median, std dev, variance, percentiles (p50, p90, p95, p99), and 95% confidence intervals.
"""

import math
from typing import List, Dict, Any
from research.models import StatisticalSummary, BenchmarkStatistics, BenchmarkReport


class StatisticalValidator:
    """
    Computes rigorous statistical distributions across latency, score, confidence, and cost.
    """

    @staticmethod
    def calculate_summary(values: List[float]) -> StatisticalSummary:
        """
        Calculates complete statistical distribution summary for a list of scalar measurements.
        """
        if not values:
            return StatisticalSummary()

        sorted_vals = sorted(values)
        n = len(sorted_vals)

        # Mean
        mean_val = sum(sorted_vals) / n

        # Median (p50)
        if n % 2 == 1:
            median_val = sorted_vals[n // 2]
        else:
            median_val = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

        # Variance & Std Dev
        if n > 1:
            variance_val = sum((x - mean_val) ** 2 for x in sorted_vals) / (n - 1)
            std_dev_val = math.sqrt(variance_val)
        else:
            variance_val = 0.0
            std_dev_val = 0.0

        # Percentiles
        def percentile(p: float) -> float:
            if n == 1:
                return sorted_vals[0]
            k = (n - 1) * (p / 100.0)
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_vals[int(k)]
            d0 = sorted_vals[int(f)] * (c - k)
            d1 = sorted_vals[int(c)] * (k - f)
            return d0 + d1

        p50_val = median_val
        p90_val = percentile(90.0)
        p95_val = percentile(95.0)
        p99_val = percentile(99.0)

        # 95% Confidence Interval (Z = 1.96)
        margin = (1.96 * std_dev_val / math.sqrt(n)) if n > 0 else 0.0
        ci_lower = mean_val - margin
        ci_upper = mean_val + margin

        return StatisticalSummary(
            mean=round(mean_val, 4),
            median=round(median_val, 4),
            std_dev=round(std_dev_val, 4),
            variance=round(variance_val, 4),
            p50=round(p50_val, 4),
            p90=round(p90_val, 4),
            p95=round(p95_val, 4),
            p99=round(p99_val, 4),
            ci_95_lower=round(ci_lower, 4),
            ci_95_upper=round(ci_upper, 4)
        )

    def evaluate_statistics(self, report: BenchmarkReport) -> BenchmarkStatistics:
        """
        Extracts sample measurements from benchmark report and computes statistical distributions.
        """
        # Collect sample values from datasets, providers, and strategies
        latencies = [d.average_latency_ms for d in report.datasets if d.average_latency_ms > 0]
        if not latencies:
            latencies = [report.average_latency_ms, report.p50_latency_ms, report.p95_latency_ms]

        scores = [d.average_score for d in report.datasets]
        if not scores:
            scores = [report.evaluation_score]

        confidences = [s.average_confidence for s in report.strategies if s.average_confidence > 0]
        if not confidences:
            confidences = [report.average_confidence]

        costs = [p.cost_usd for p in report.providers if p.cost_usd > 0]
        if not costs:
            costs = [report.estimated_cost_usd]

        return BenchmarkStatistics(
            latency_ms=self.calculate_summary(latencies),
            score=self.calculate_summary(scores),
            confidence=self.calculate_summary(confidences),
            cost_usd=self.calculate_summary(costs)
        )
