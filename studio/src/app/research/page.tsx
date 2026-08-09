"use client";

import React, { useState, useEffect } from "react";
import {
  Shield,
  Trophy,
  Database,
  Cpu,
  Zap,
  Activity,
  DollarSign,
  Clock,
  Play,
  RefreshCw,
  CheckCircle,
  FileCheck,
  GitCommit,
  Layers,
  BarChart2,
  Lock
} from "lucide-react";

interface DatasetMetric {
  dataset_id: string;
  records: number;
  executed: number;
  success_rate: number;
  average_score: number;
  average_latency_ms: number;
  provider: string;
}

interface ProviderMetric {
  provider_id: string;
  attacks: number;
  success_rate: number;
  refusal_rate: number;
  average_latency_ms: number;
  cost_usd: number;
  evaluation_score: number;
  rank: number;
}

interface StrategyMetric {
  strategy_family: string;
  attacks: number;
  success_rate: number;
  average_confidence: number;
  average_score: number;
  average_latency_ms: number;
  rank: number;
}

interface SwarmMetric {
  agent_name: string;
  attacks: number;
  success_rate: number;
  failures: number;
  average_score: number;
  average_cost_usd: number;
  average_latency_ms: number;
  rank: number;
}

interface ProvenanceRecord {
  benchmark_uuid: string;
  git_commit_hash: string;
  python_version: string;
  os_info: str;
  orchestrator_version: string;
  dataset_checksums: Record<string, string>;
}

interface PublicationChecklist {
  datasets_available: boolean;
  reports_generated: boolean;
  tests_passing: boolean;
  coverage_threshold_met: boolean;
  benchmark_completed: boolean;
  provenance_generated: boolean;
  reproducibility_generated: boolean;
  integrity_verified: boolean;
  publication_ready: boolean;
  reasons: string[];
}

interface StatisticalSummary {
  mean: number;
  median: number;
  std_dev: number;
  p90: number;
  p95: number;
  p99: number;
  ci_95_lower: number;
  ci_95_upper: number;
}

interface BenchmarkStatistics {
  latency_ms: StatisticalSummary;
  score: StatisticalSummary;
  confidence: StatisticalSummary;
  cost_usd: StatisticalSummary;
}

interface BenchmarkReport {
  benchmark_id: string;
  timestamp: string;
  status: string;
  overall_health: string;
  total_execution_time_sec: number;
  attacks_executed: number;
  successful_attacks: number;
  failed_attacks: number;
  refusal_rate: number;
  average_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  evaluation_score: number;
  estimated_cost_usd: number;
  datasets: DatasetMetric[];
  providers: ProviderMetric[];
  strategies: StrategyMetric[];
  swarm_agents: SwarmMetric[];
  provenance?: ProvenanceRecord;
  checklist?: PublicationChecklist;
  statistics?: BenchmarkStatistics;
  artifact_hashes?: Record<string, string>;
}

export default function ResearchBenchmarkingPage() {
  const [report, setReport] = useState<BenchmarkReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"leaderboards" | "validation" | "statistics" | "hashes">("validation");

  const fetchResearchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/research");
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      } else {
        setError("Failed to fetch research benchmark data");
      }
    } catch (err: any) {
      setError(err.message || "Failed to load research data");
    } finally {
      setLoading(false);
    }
  };

  const triggerBenchmarkRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/research/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          objective: "Studio Interactive Scientific Benchmark & Reproducibility Validation Run",
          max_attacks_per_dataset: 5,
          parallelism: 4
        })
      });
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      } else {
        setError("Benchmark execution failed");
      }
    } catch (err: any) {
      setError(err.message || "Execution failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResearchData();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              <Trophy className="w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight font-heading">
              Research & Benchmark Harness
            </h1>
          </div>
          <p className="text-slate-400 text-sm mt-1 font-sans">
            End-to-End Autonomous AI Attack Benchmark & Scientific Reproducibility Platform
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchResearchData}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg font-medium text-sm border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            Refresh Data
          </button>
          <button
            onClick={triggerBenchmarkRun}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium text-sm shadow-md transition"
          >
            <Play className="w-4 h-4" />
            Execute Benchmark
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-sm">
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab("validation")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "validation"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800"
          }`}
        >
          <CheckCircle className="w-4 h-4" />
          Publication Validation & Integrity
        </button>
        <button
          onClick={() => setActiveTab("leaderboards")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "leaderboards"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800"
          }`}
        >
          <Trophy className="w-4 h-4" />
          Leaderboards
        </button>
        <button
          onClick={() => setActiveTab("statistics")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "statistics"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800"
          }`}
        >
          <BarChart2 className="w-4 h-4" />
          Statistical Validation
        </button>
        <button
          onClick={() => setActiveTab("hashes")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "hashes"
              ? "bg-indigo-600 text-white"
              : "text-slate-400 hover:text-white hover:bg-slate-800"
          }`}
        >
          <Lock className="w-4 h-4" />
          Artifact SHA256 Hashes
        </button>
      </div>

      {/* TAB 1: Publication Validation & Integrity */}
      {activeTab === "validation" && (
        <div className="space-y-6">
          {/* Publication Readiness Card */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-emerald-400" />
                <h2 className="text-lg font-bold text-white font-heading">
                  Scientific Research Publication Readiness Checklist
                </h2>
              </div>
              <span
                className={`px-3 py-1 rounded-full text-xs font-mono font-bold uppercase border ${
                  report?.checklist?.publication_ready
                    ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/40"
                    : "bg-rose-500/20 text-rose-400 border-rose-500/40"
                }`}
              >
                {report?.checklist?.publication_ready ? "PUBLICATION READY" : "NOT READY"}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800">
                <div className="text-xs text-slate-400 font-mono">GATE 1: DATASETS</div>
                <div className="text-sm font-bold text-emerald-400 mt-1">
                  {report?.checklist?.datasets_available ? "VERIFIED" : "FAILED"}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800">
                <div className="text-xs text-slate-400 font-mono">GATE 2: REPORTS</div>
                <div className="text-sm font-bold text-emerald-400 mt-1">
                  {report?.checklist?.reports_generated ? "VERIFIED" : "FAILED"}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800">
                <div className="text-xs text-slate-400 font-mono">GATE 6: PROVENANCE</div>
                <div className="text-sm font-bold text-emerald-400 mt-1">
                  {report?.checklist?.provenance_generated ? "VERIFIED" : "FAILED"}
                </div>
              </div>
              <div className="p-3 rounded-lg bg-slate-800/40 border border-slate-800">
                <div className="text-xs text-slate-400 font-mono">GATE 7: REPRODUCIBILITY</div>
                <div className="text-sm font-bold text-emerald-400 mt-1">
                  {report?.checklist?.reproducibility_generated ? "VERIFIED" : "FAILED"}
                </div>
              </div>
            </div>
          </div>

          {/* Provenance Context Card */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
            <div className="flex items-center gap-2">
              <GitCommit className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-bold text-white font-heading">
                Scientific Provenance & Environment Record
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-slate-300 font-mono">
              <div>
                <span className="text-slate-400 block text-xs">GIT COMMIT HASH</span>
                <span className="text-white font-bold">{report?.provenance?.git_commit_hash}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">PYTHON RUNTIME</span>
                <span className="text-white font-bold">{report?.provenance?.python_version}</span>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">OS PLATFORM</span>
                <span className="text-white font-bold">{report?.provenance?.os_info}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: Leaderboards */}
      {activeTab === "leaderboards" && (
        <div className="space-y-6">
          {/* Metric Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
              <div className="flex justify-between items-center text-slate-400 text-xs font-medium font-mono">
                <span>EXECUTED ATTACKS</span>
                <Activity className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2 font-mono">
                {report ? report.attacks_executed : "-"}
              </div>
            </div>

            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
              <div className="flex justify-between items-center text-slate-400 text-xs font-medium font-mono">
                <span>AVG LATENCY (P95)</span>
                <Clock className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2 font-mono">
                {report ? `${report.average_latency_ms.toFixed(1)} ms` : "-"}
              </div>
            </div>

            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
              <div className="flex justify-between items-center text-slate-400 text-xs font-medium font-mono">
                <span>EVALUATION SCORE</span>
                <Zap className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-bold text-emerald-400 mt-2 font-mono">
                {report ? report.evaluation_score.toFixed(2) : "-"}
              </div>
            </div>

            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
              <div className="flex justify-between items-center text-slate-400 text-xs font-medium font-mono">
                <span>ESTIMATED COST</span>
                <DollarSign className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="text-2xl font-bold text-white mt-2 font-mono">
                {report ? `$${report.estimated_cost_usd.toFixed(4)}` : "-"}
              </div>
            </div>
          </div>

          {/* Dataset Leaderboard Table */}
          <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-indigo-400" />
              <h2 className="text-lg font-bold text-white font-heading">Dataset Leaderboard</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300 border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 text-xs font-mono uppercase bg-slate-800/40">
                    <th className="py-3 px-4">Dataset</th>
                    <th className="py-3 px-4">Records</th>
                    <th className="py-3 px-4">Executed</th>
                    <th className="py-3 px-4">Success %</th>
                    <th className="py-3 px-4">Avg Score</th>
                    <th className="py-3 px-4">Avg Latency</th>
                    <th className="py-3 px-4">Provider</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-sans">
                  {report?.datasets.map((d) => (
                    <tr key={d.dataset_id} className="hover:bg-slate-800/30 transition">
                      <td className="py-3 px-4 font-semibold text-white font-mono">{d.dataset_id}</td>
                      <td className="py-3 px-4">{d.records}</td>
                      <td className="py-3 px-4">{d.executed}</td>
                      <td className="py-3 px-4 text-emerald-400 font-mono font-medium">
                        {(d.success_rate * 100).toFixed(1)}%
                      </td>
                      <td className="py-3 px-4 font-mono">{d.average_score.toFixed(2)}</td>
                      <td className="py-3 px-4 font-mono">{d.average_latency_ms.toFixed(1)} ms</td>
                      <td className="py-3 px-4 text-slate-400">{d.provider}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: Statistical Validation */}
      {activeTab === "statistics" && (
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
          <div className="flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-bold text-white font-heading">
              Statistical Validation Distributions
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 text-xs font-mono uppercase">
                  <th className="py-3 px-4">Metric</th>
                  <th className="py-3 px-4">Mean</th>
                  <th className="py-3 px-4">Median (P50)</th>
                  <th className="py-3 px-4">Std Dev</th>
                  <th className="py-3 px-4">P90</th>
                  <th className="py-3 px-4">P95</th>
                  <th className="py-3 px-4">95% CI Lower</th>
                  <th className="py-3 px-4">95% CI Upper</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                <tr>
                  <td className="py-3 px-4 font-bold text-white">Latency (ms)</td>
                  <td className="py-3 px-4">{report?.statistics?.latency_ms.mean.toFixed(2)}</td>
                  <td className="py-3 px-4">{report?.statistics?.latency_ms.median.toFixed(2)}</td>
                  <td className="py-3 px-4">{report?.statistics?.latency_ms.std_dev.toFixed(2)}</td>
                  <td className="py-3 px-4">{report?.statistics?.latency_ms.p90.toFixed(2)}</td>
                  <td className="py-3 px-4 text-amber-400">{report?.statistics?.latency_ms.p95.toFixed(2)}</td>
                  <td className="py-3 px-4">{report?.statistics?.latency_ms.ci_95_lower.toFixed(2)}</td>
                  <td className="py-3 px-4">{report?.statistics?.latency_ms.ci_95_upper.toFixed(2)}</td>
                </tr>
                <tr>
                  <td className="py-3 px-4 font-bold text-white">Score</td>
                  <td className="py-3 px-4">{report?.statistics?.score.mean.toFixed(4)}</td>
                  <td className="py-3 px-4">{report?.statistics?.score.median.toFixed(4)}</td>
                  <td className="py-3 px-4">{report?.statistics?.score.std_dev.toFixed(4)}</td>
                  <td className="py-3 px-4">{report?.statistics?.score.p90.toFixed(4)}</td>
                  <td className="py-3 px-4 text-emerald-400">{report?.statistics?.score.p95.toFixed(4)}</td>
                  <td className="py-3 px-4">{report?.statistics?.score.ci_95_lower.toFixed(4)}</td>
                  <td className="py-3 px-4">{report?.statistics?.score.ci_95_upper.toFixed(4)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 4: Artifact SHA256 Hashes */}
      {activeTab === "hashes" && (
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
          <div className="flex items-center gap-2">
            <Lock className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-white font-heading">
              Artifact SHA256 Signature Hashes
            </h2>
          </div>
          <div className="space-y-2 font-mono text-xs max-h-[400px] overflow-y-auto">
            {report?.artifact_hashes &&
              Object.entries(report.artifact_hashes).map(([path, sha]) => (
                <div key={path} className="flex justify-between p-2 rounded bg-slate-800/40 border border-slate-800">
                  <span className="text-slate-300">{path}</span>
                  <span className="text-amber-400 font-bold">{sha}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
