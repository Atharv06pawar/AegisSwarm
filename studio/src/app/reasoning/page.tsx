"use client";

import React, { useState, useEffect } from "react";

interface StrategyCandidate {
  candidate_id: string;
  attack_family: string;
  mutation_family: string;
  provider: string;
  model: string;
  estimated_cost: number;
  estimated_latency_ms: number;
  estimated_success: number;
  estimated_severity: string;
  estimated_confidence: number;
  reasoning_text: string;
  rank_score?: number;
}

interface ProviderRecommendation {
  recommended_provider: string;
  recommended_model: string;
  confidence_score: number;
  estimated_latency_ms: number;
  estimated_cost_usd: number;
  rationale: string;
}

interface SimilarityMatch {
  record_id: string;
  attack_id: string;
  dataset: string;
  provider: string;
  model: string;
  taxonomy_node: string;
  similarity_score: number;
  matched_features: string[];
}

interface ReflectionResult {
  reflection_id: string;
  what_worked: string;
  what_failed: string;
  why_outcome: str;
  how_to_improve: string;
  timestamp: string;
}

interface ReasoningResponse {
  request_id: string;
  chosen_strategy: StrategyCandidate;
  all_candidates: StrategyCandidate[];
  similarity_matches: SimilarityMatch[];
  provider_recommendation: ProviderRecommendation;
  mutation_plan: {
    chain: string[];
    expected_evasion_rate: number;
  };
  reflections: ReflectionResult[];
  timeline: Array<{ step_name: string; duration_ms: number }>;
  overall_confidence: number;
}

export default function ReasoningDashboardPage() {
  const [objective, setObjective] = useState("Evaluate multi-turn agent guardrail compliance");
  const [targetProvider, setTargetProvider] = useState("openai");
  const [data, setData] = useState<ReasoningResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlan = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/reasoning/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          objective: objective,
          target_provider: targetProvider,
          target_model: "gpt-4o",
          max_candidates: 5,
        }),
      });
      if (!res.ok) {
        throw new Error(`Reasoning API responded with status ${res.status}`);
      }
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || "Failed to trigger semantic reasoning pass");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlan();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 via-teal-300 to-indigo-400 bg-clip-text text-transparent">
            Semantic Reasoning & Autonomous Strategy Engine
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            LLM-Driven Strategic Planning, Candidate Generation, Self-Critique & Reflection
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="text"
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-sm rounded-lg px-4 py-2 w-80 focus:outline-none focus:border-cyan-500"
            placeholder="Enter attack objective..."
          />
          <button
            onClick={fetchPlan}
            disabled={loading}
            className="bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium px-5 py-2 rounded-lg transition shadow-lg shadow-cyan-950 flex items-center gap-2"
          >
            {loading ? "Reasoning..." : "Synthesize Plan"}
          </button>
        </div>
      </header>

      {error && (
        <div className="bg-red-950/50 border border-red-800 text-red-300 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {data && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chosen Strategy & Confidence */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-cyan-300">Chosen Optimal Strategy</h2>
                <span className="bg-cyan-950 text-cyan-400 border border-cyan-800 text-xs font-semibold px-3 py-1 rounded-full">
                  Confidence: {(data.overall_confidence * 100).toFixed(1)}%
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-400">Attack Family</div>
                  <div className="text-base font-bold text-slate-200">{data.chosen_strategy.attack_family}</div>
                </div>
                <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-400">Mutation Family</div>
                  <div className="text-base font-bold text-slate-200">{data.chosen_strategy.mutation_family}</div>
                </div>
                <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-400">Target Provider</div>
                  <div className="text-base font-bold text-slate-200">{data.chosen_strategy.provider}</div>
                </div>
                <div className="bg-slate-950/80 p-3 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-400">Est. Success</div>
                  <div className="text-base font-bold text-emerald-400">
                    {(data.chosen_strategy.estimated_success * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="text-sm text-slate-300 bg-slate-950 p-4 rounded-lg border border-slate-800">
                <div className="text-xs text-slate-400 font-semibold mb-1">Strategic Rationale:</div>
                {data.chosen_strategy.reasoning_text}
              </div>
            </div>

            {/* Generated Candidates Table */}
            <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl">
              <h2 className="text-xl font-semibold text-slate-200 mb-4">Generated Strategy Candidates</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Family</th>
                      <th className="py-3 px-4">Mutation</th>
                      <th className="py-3 px-4">Provider</th>
                      <th className="py-3 px-4">Success</th>
                      <th className="py-3 px-4">Cost</th>
                      <th className="py-3 px-4">Rank Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {data.all_candidates.map((cand) => (
                      <tr key={cand.candidate_id} className="hover:bg-slate-800/50 transition">
                        <td className="py-3 px-4 font-medium text-slate-200">{cand.attack_family}</td>
                        <td className="py-3 px-4 text-cyan-400">{cand.mutation_family}</td>
                        <td className="py-3 px-4 text-slate-300">{cand.provider}</td>
                        <td className="py-3 px-4 text-emerald-400">{(cand.estimated_success * 100).toFixed(0)}%</td>
                        <td className="py-3 px-4 text-slate-400">${cand.estimated_cost.toFixed(4)}</td>
                        <td className="py-3 px-4 font-bold text-amber-400">{cand.rank_score ?? "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Sidebar: Mutation Chain, Provider Rec, Timeline */}
          <div className="space-y-6">
            {/* Mutation Chain */}
            <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl">
              <h3 className="text-lg font-semibold text-slate-200 mb-3">Mutation Transformation Chain</h3>
              <div className="flex flex-wrap gap-2 mb-3">
                {data.mutation_plan.chain.map((m, idx) => (
                  <span
                    key={idx}
                    className="bg-indigo-950 text-indigo-300 border border-indigo-800 text-xs px-2.5 py-1 rounded"
                  >
                    {m} {idx < data.mutation_plan.chain.length - 1 ? "→" : ""}
                  </span>
                ))}
              </div>
              <div className="text-xs text-slate-400">
                Expected Evasion Rate:{" "}
                <span className="text-emerald-400 font-bold">
                  {(data.mutation_plan.expected_evasion_rate * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            {/* Provider Recommendation */}
            <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl">
              <h3 className="text-lg font-semibold text-slate-200 mb-3">Provider Recommendation</h3>
              <div className="bg-slate-950 p-3 rounded border border-slate-800 mb-2 text-sm text-cyan-300 font-medium">
                {data.provider_recommendation.recommended_provider}:
                {data.provider_recommendation.recommended_model}
              </div>
              <p className="text-xs text-slate-400">{data.provider_recommendation.rationale}</p>
            </div>

            {/* Reasoning Timeline */}
            <div className="bg-slate-900/70 backdrop-blur-md border border-slate-800 rounded-xl p-6 shadow-xl">
              <h3 className="text-lg font-semibold text-slate-200 mb-3">Reasoning Timeline</h3>
              <ul className="space-y-2 text-xs">
                {data.timeline.map((t, idx) => (
                  <li key={idx} className="flex justify-between items-center bg-slate-950 p-2 rounded border border-slate-800">
                    <span className="text-slate-300">{t.step_name}</span>
                    <span className="text-cyan-400 font-mono">{t.duration_ms.toFixed(1)} ms</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
