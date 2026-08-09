'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function TelemetryDashboardPage() {
  const [telemetry, setTelemetry] = useState<any>({
    system_status: 'healthy',
    active_campaigns: 1,
    running_workers: 4,
    requests_per_sec: 14.5,
    attacks_per_min: 120.0,
    latency: {
      average: 45.2,
      p95: 120.5,
      p99: 250.0
    },
    provider_status: {
      openai: { status: 'healthy', latency_ms: 45.2 },
      anthropic: { status: 'healthy', latency_ms: 55.0 },
      gemini: { status: 'healthy', latency_ms: 38.0 },
      ollama: { status: 'healthy', latency_ms: 12.0 },
      openrouter: { status: 'healthy', latency_ms: 60.0 }
    },
    recent_events: [
      { event_id: 'ev-1', event_type: 'ExecutionFinished', component: 'execution', timestamp: new Date().toISOString() },
      { event_id: 'ev-2', event_type: 'JailbreakDetected', component: 'evaluation', timestamp: new Date().toISOString() }
    ]
  });

  return (
    <div className="p-8 space-y-6 text-slate-100 bg-slate-950 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Live Telemetry & Observability Command Center</h1>
          <p className="text-slate-400 text-sm">
            Real-time telemetry streams, distributed traces, provider status, and operational metrics.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs text-emerald-400 font-mono font-medium">LIVE POLL (2s)</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">System Status</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1 uppercase">{telemetry.system_status}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Requests / Sec</p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">{telemetry.requests_per_sec} req/s</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">P95 / P99 Latency</p>
          <p className="text-2xl font-bold text-purple-400 mt-1">{telemetry.latency.p95}ms / {telemetry.latency.p99}ms</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Active Campaigns / Workers</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">{telemetry.active_campaigns} / {telemetry.running_workers}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-4">
          <h3 className="font-semibold text-cyan-400 border-b border-slate-800 pb-2">Provider Status & Latencies</h3>
          <div className="space-y-2 text-xs">
            {Object.entries(telemetry.provider_status).map(([prov, details]: [string, any]) => (
              <div key={prov} className="flex justify-between items-center bg-slate-950 p-2.5 rounded border border-slate-800">
                <span className="font-medium text-slate-200 uppercase">{prov}</span>
                <div className="flex items-center space-x-3 font-mono">
                  <span className="text-slate-400">{details.latency_ms} ms</span>
                  <span className="text-emerald-400 bg-emerald-950/50 px-2 py-0.5 rounded text-[10px] border border-emerald-800">
                    {details.status.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-4">
          <h3 className="font-semibold text-purple-400 border-b border-slate-800 pb-2">Live Event Timeline</h3>
          <div className="space-y-2 text-xs font-mono">
            {telemetry.recent_events.map((ev: any) => (
              <div key={ev.event_id} className="bg-slate-950 p-2.5 rounded border border-slate-800 flex justify-between">
                <div>
                  <span className="text-cyan-400 font-bold">[{ev.component.toUpperCase()}]</span>{' '}
                  <span className="text-slate-200">{ev.event_type}</span>
                </div>
                <span className="text-slate-500 text-[10px]">{new Date(ev.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
