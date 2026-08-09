'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function LearningDashboardPage() {
  const [learningData, setLearningData] = useState<any>({
    status: 'active',
    statistics: {
      total_records: 1250,
      overall_success_rate: 0.824,
      average_score: 0.885,
      top_mutations: {
        indirect_injection: 420,
        roleplay: 310,
        persona: 250,
        delimiter: 180
      },
      top_agents: {
        jailbreak: 480,
        indirect_injection: 390,
        roleplay: 210
      }
    },
    rankings: [
      { strategy: 'indirect_injection', utility_score: 0.92 },
      { strategy: 'roleplay', utility_score: 0.88 },
      { strategy: 'persona', utility_score: 0.84 },
      { strategy: 'delimiter', utility_score: 0.79 },
      { strategy: 'encoding', utility_score: 0.72 }
    ]
  });

  return (
    <div className="p-8 space-y-6 text-slate-100 bg-slate-950 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Autonomous Learning & Adaptive Strategy Control</h1>
          <p className="text-slate-400 text-sm">
            Feedback-driven Q-learning, mutation ranking, replay fidelity, and attack graph exploration.
          </p>
        </div>
        <div className="flex space-x-3">
          <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-medium text-xs">
            Run Strategy Optimization
          </button>
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-medium text-xs">
            Replay Campaign
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Engine Status</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1 uppercase">{learningData.status}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Historical Memory Records</p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">{learningData.statistics.total_records}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Overall Attack Success Rate</p>
          <p className="text-2xl font-bold text-purple-400 mt-1">{(learningData.statistics.overall_success_rate * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Average Utility Score</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">{learningData.statistics.average_score}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-4">
          <h3 className="font-semibold text-cyan-400 border-b border-slate-800 pb-2">Strategy Utility Rankings</h3>
          <div className="space-y-2 text-xs font-mono">
            {learningData.rankings.map((rk: any, idx: number) => (
              <div key={rk.strategy} className="flex justify-between items-center bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="font-semibold text-slate-200">#{idx + 1} {rk.strategy.toUpperCase()}</span>
                <span className="text-emerald-400 font-bold">Score: {rk.utility_score}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-4">
          <h3 className="font-semibold text-purple-400 border-b border-slate-800 pb-2">Top Successful Mutation Families</h3>
          <div className="space-y-2 text-xs font-mono">
            {Object.entries(learningData.statistics.top_mutations).map(([mut, count]: [string, any]) => (
              <div key={mut} className="flex justify-between items-center bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="font-semibold text-slate-200">{mut}</span>
                <span className="text-cyan-400 font-bold">{count} Hits</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
