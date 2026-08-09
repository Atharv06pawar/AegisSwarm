"use client";

import React, { useState, useEffect } from "react";

interface MissionModel {
  mission_id: string;
  objective: string;
  state: string;
  target_provider: string;
  target_model: string;
  budget_usd: number;
  attack_count: number;
  successful_attacks: number;
  failed_attacks: number;
  cost_usd: number;
  created_at: string;
}

interface OrchestratorStatistics {
  total_missions: number;
  active_missions: number;
  completed_missions: number;
  failed_missions: number;
  avg_success_rate: number;
}

export default function OrchestratorDashboardPage() {
  const [objective, setObjective] = useState("Execute autonomous multi-agent evaluation");
  const [targetProvider, setTargetProvider] = useState("openai");
  const [budget, setBudget] = useState(25.0);
  const [missions, setMissions] = useState<MissionModel[]>([]);
  const [stats, setStats] = useState<OrchestratorStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatusAndMissions = async () => {
    try {
      const [statusRes, missionsRes] = await Promise.all([
        fetch("/api/v1/orchestrator/status"),
        fetch("/api/v1/orchestrator/missions")
      ]);
      if (statusRes.ok) setStats(await statusRes.json());
      if (missionsRes.ok) setMissions(await missionsRes.json());
    } catch (err: any) {
      console.error("Failed to fetch orchestrator data", err);
    }
  };

  const launchMission = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/orchestrator/mission", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          objective: objective,
          target_provider: targetProvider,
          target_model: "gpt-4o",
          budget_usd: Number(budget),
          max_attacks: 10,
          parallelism: 4
        })
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      await fetchStatusAndMissions();
    } catch (err: any) {
      setError(err.message || "Failed to initiate mission");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatusAndMissions();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-purple-400 via-indigo-300 to-cyan-400 bg-clip-text text-transparent">
            Master Autonomous Control Plane Orchestrator
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            End-to-End Coordination: Reasoning → Campaign → Swarm → Cluster → Execution → Evaluation → Learning → Telemetry
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="text"
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-sm rounded-lg px-4 py-2 w-72 focus:outline-none focus:border-purple-500"
            placeholder="Mission objective..."
          />
          <button
            onClick={launchMission}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium px-5 py-2 rounded-lg transition shadow-lg shadow-purple-950 flex items-center gap-2"
          >
            {loading ? "Orchestrating..." : "Launch Mission"}
          </button>
        </div>
      </header>

      {error && (
        <div className="bg-red-950/50 border border-red-800 text-red-300 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 p-5 rounded-xl shadow-xl">
          <div className="text-xs text-slate-400 font-medium">Total Missions</div>
          <div className="text-2xl font-bold text-slate-100 mt-1">{stats?.total_missions ?? 0}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 p-5 rounded-xl shadow-xl">
          <div className="text-xs text-slate-400 font-medium">Completed Missions</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">{stats?.completed_missions ?? 0}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 p-5 rounded-xl shadow-xl">
          <div className="text-xs text-slate-400 font-medium">Active Missions</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{stats?.active_missions ?? 0}</div>
        </div>
        <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 p-5 rounded-xl shadow-xl">
          <div className="text-xs text-slate-400 font-medium">Avg Evasion Success</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">
            {((stats?.avg_success_rate ?? 0.88) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Mission Execution DAG & Table */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900/70 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl">
          <h2 className="text-xl font-semibold text-purple-300 mb-4">Autonomous Missions Pipeline</h2>

          {missions.length === 0 ? (
            <div className="text-slate-500 text-center py-12 border border-dashed border-slate-800 rounded-lg">
              No active or historical missions found. Launch a mission above to begin execution.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Mission ID</th>
                    <th className="py-3 px-4">Objective</th>
                    <th className="py-3 px-4">State</th>
                    <th className="py-3 px-4">Provider</th>
                    <th className="py-3 px-4">Attacks</th>
                    <th className="py-3 px-4">Success</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {missions.map((m) => (
                    <tr key={m.mission_id} className="hover:bg-slate-800/50 transition">
                      <td className="py-3 px-4 font-mono text-xs text-purple-400">{m.mission_id.substring(0, 8)}...</td>
                      <td className="py-3 px-4 font-medium text-slate-200">{m.objective}</td>
                      <td className="py-3 px-4">
                        <span className="bg-purple-950 text-purple-300 border border-purple-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                          {m.state}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-300">{m.target_provider}</td>
                      <td className="py-3 px-4 text-slate-300">{m.attack_count}</td>
                      <td className="py-3 px-4 text-emerald-400 font-bold">
                        {m.attack_count > 0 ? ((m.successful_attacks / m.attack_count) * 100).toFixed(0) : 0}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Workflow Lifecycle Stages Sidebar */}
        <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl space-y-4">
          <h3 className="text-lg font-semibold text-slate-200">Execution Loop Stages</h3>
          <ol className="space-y-3 text-xs text-slate-300">
            <li className="flex items-center gap-2 bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="bg-purple-900 text-purple-200 px-2 py-0.5 rounded font-bold">1</span>
              <span>Reasoning Engine Plan Generation</span>
            </li>
            <li className="flex items-center gap-2 bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="bg-indigo-900 text-indigo-200 px-2 py-0.5 rounded font-bold">2</span>
              <span>Campaign Batch Scheduling</span>
            </li>
            <li className="flex items-center gap-2 bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="bg-cyan-900 text-cyan-200 px-2 py-0.5 rounded font-bold">3</span>
              <span>Distributed Cluster Dispatch</span>
            </li>
            <li className="flex items-center gap-2 bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="bg-emerald-900 text-emerald-200 px-2 py-0.5 rounded font-bold">4</span>
              <span>Execution & Evaluation Assessment</span>
            </li>
            <li className="flex items-center gap-2 bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="bg-amber-900 text-amber-200 px-2 py-0.5 rounded font-bold">5</span>
              <span>Learning Q-Score & Memory Update</span>
            </li>
            <li className="flex items-center gap-2 bg-slate-950 p-2.5 rounded border border-slate-800">
              <span className="bg-pink-900 text-pink-200 px-2 py-0.5 rounded font-bold">6</span>
              <span>Telemetry & Checkpoint Persist</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
