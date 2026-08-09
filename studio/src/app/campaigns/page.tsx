'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface CampaignConfig {
  campaign_id: string;
  name: string;
  creation_timestamp: string;
  maximum_attacks: number;
  parallel_workers: number;
  budget: {
    max_cost_usd: number;
    current_cost_usd: number;
  };
}

export default function CampaignDashboard() {
  const [campaigns, setCampaigns] = useState<CampaignConfig[]>([
    {
      campaign_id: 'a1b2c3d4-0000-4000-8000-000000000001',
      name: 'Production LLM Red-Team Campaign 2026',
      creation_timestamp: new Date().toISOString(),
      maximum_attacks: 500,
      parallel_workers: 8,
      budget: {
        max_cost_usd: 100.0,
        current_cost_usd: 12.45
      }
    }
  ]);

  return (
    <div className="p-8 space-y-6 text-slate-100 bg-slate-950 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Distributed Campaign Command Center</h1>
          <p className="text-slate-400 text-sm">
            Orchestrate multi-provider, multi-agent autonomous attack swarms across large workloads.
          </p>
        </div>
        <button className="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded font-medium shadow">
          + Create New Campaign
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Active Campaigns</p>
          <p className="text-2xl font-bold text-white mt-1">{campaigns.length}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Total Workers Allocated</p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">8 Workers</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Total Budget Spent</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1">$12.45 / $100.00</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Provider Targets</p>
          <p className="text-2xl font-bold text-purple-400 mt-1">OpenAI, Anthropic</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-800 font-semibold text-slate-200">
          Registered Distributed Campaigns
        </div>
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-950 text-slate-400 text-xs uppercase border-b border-slate-800">
              <th className="px-6 py-3">Campaign Name</th>
              <th className="px-6 py-3">Campaign ID</th>
              <th className="px-6 py-3">Workers</th>
              <th className="px-6 py-3">Budget Spent</th>
              <th className="px-6 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-sm">
            {campaigns.map((c) => (
              <tr key={c.campaign_id} className="hover:bg-slate-800/50 transition">
                <td className="px-6 py-4 font-medium text-white">{c.name}</td>
                <td className="px-6 py-4 text-xs font-mono text-slate-400">{c.campaign_id}</td>
                <td className="px-6 py-4 text-slate-300">{c.parallel_workers} Workers</td>
                <td className="px-6 py-4 text-emerald-400 font-mono">${c.budget.current_cost_usd} / ${c.budget.max_cost_usd}</td>
                <td className="px-6 py-4">
                  <Link
                    href={`/campaigns/${c.campaign_id}`}
                    className="text-cyan-400 hover:underline font-medium text-xs"
                  >
                    View Details & Live Monitor →
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
