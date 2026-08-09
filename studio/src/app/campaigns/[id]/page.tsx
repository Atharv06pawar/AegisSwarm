'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function CampaignDetailsPage({ params }: { params: { id: string } }) {
  const campaignId = params.id;
  const [status, setStatus] = useState<'running' | 'paused' | 'completed' | 'cancelled'>('running');

  return (
    <div className="p-8 space-y-6 text-slate-100 bg-slate-950 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <Link href="/campaigns" className="text-cyan-400 text-xs hover:underline">← Back to Campaigns</Link>
          <h1 className="text-3xl font-bold text-white mt-1">Campaign Details & Live Monitor</h1>
          <p className="text-xs text-slate-400 font-mono mt-1">UUID: {campaignId}</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setStatus('running')}
            className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded text-xs font-semibold"
          >
            Start / Resume
          </button>
          <button
            onClick={() => setStatus('paused')}
            className="bg-amber-600 hover:bg-amber-500 text-white px-3 py-1.5 rounded text-xs font-semibold"
          >
            Pause
          </button>
          <button
            onClick={() => setStatus('cancelled')}
            className="bg-rose-600 hover:bg-rose-500 text-white px-3 py-1.5 rounded text-xs font-semibold"
          >
            Cancel
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-3">
          <h3 className="font-semibold text-cyan-400 border-b border-slate-800 pb-2">Worker Monitor</h3>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between bg-slate-950 p-2 rounded border border-slate-800">
              <span>Worker #1 (OpenAI / gpt-4o)</span>
              <span className="text-emerald-400 font-mono">BUSY</span>
            </div>
            <div className="flex justify-between bg-slate-950 p-2 rounded border border-slate-800">
              <span>Worker #2 (Anthropic / claude-3)</span>
              <span className="text-emerald-400 font-mono">BUSY</span>
            </div>
            <div className="flex justify-between bg-slate-950 p-2 rounded border border-slate-800">
              <span>Worker #3 (Gemini / gemini-1.5)</span>
              <span className="text-slate-400 font-mono">IDLE</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-3">
          <h3 className="font-semibold text-emerald-400 border-b border-slate-800 pb-2">Budget Dashboard</h3>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Max USD Limit:</span>
              <span className="font-mono text-white">$100.00</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Spent USD:</span>
              <span className="font-mono text-emerald-400">$12.45</span>
            </div>
            <div className="w-full bg-slate-950 h-2 rounded overflow-hidden mt-2">
              <div className="bg-emerald-500 h-full w-[12%]"></div>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-3">
          <h3 className="font-semibold text-purple-400 border-b border-slate-800 pb-2">Live Progress Timeline</h3>
          <div className="space-y-1 text-xs text-slate-300">
            <p>✔ Campaign initialized & workers allocated</p>
            <p>✔ Checkpoint saved (atomic sync)</p>
            <p className="text-cyan-400 font-mono">⚡ 48 attacks executed (84% success rate)</p>
          </div>
        </div>
      </div>
    </div>
  );
}
