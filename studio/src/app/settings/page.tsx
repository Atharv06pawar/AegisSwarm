"use client";

import React, { useState } from "react";
import { Settings as SettingsIcon, Save, Key, HardDrive, Cpu, Radio, Moon } from "lucide-react";

export default function PlatformSettingsPage() {
  const [workers, setWorkers] = useState("4");
  const [cpuThreads, setCpuThreads] = useState("8");
  const [gpuAcceleration, setGpuAcceleration] = useState(true);
  const [telemetryEnabled, setTelemetryEnabled] = useState(true);
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 space-y-6 max-w-[1200px] mx-auto">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-heading">Platform System Settings</h1>
          <p className="text-slate-400 text-sm mt-1">Configure Storage, Distributed Cluster Workers, GPU Acceleration & Telemetry</p>
        </div>
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm rounded-lg shadow-md transition"
        >
          <Save className="w-4 h-4" /> Save Settings
        </button>
      </div>

      {saved && (
        <div className="p-3 rounded bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 text-sm font-mono">
          ✓ System Settings Saved Successfully!
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Distributed Cluster Workers */}
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
          <div className="flex items-center gap-2 text-white font-bold font-heading">
            <Cpu className="w-5 h-5 text-indigo-400" /> Distributed Workers & Processing
          </div>
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-400 font-mono block mb-1">PARALLEL WORKERS</label>
              <input
                type="number"
                value={workers}
                onChange={(e) => setWorkers(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded text-sm font-mono"
              />
            </div>
            <div>
              <label className="text-xs text-slate-400 font-mono block mb-1">CPU THREADS PER WORKER</label>
              <input
                type="number"
                value={cpuThreads}
                onChange={(e) => setCpuThreads(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded text-sm font-mono"
              />
            </div>
            <div className="flex items-center justify-between pt-2">
              <span className="text-sm text-slate-300">GPU Acceleration</span>
              <input
                type="checkbox"
                checked={gpuAcceleration}
                onChange={(e) => setGpuAcceleration(e.target.checked)}
                className="w-4 h-4 text-indigo-600 rounded"
              />
            </div>
          </div>
        </div>

        {/* Telemetry & Observability */}
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
          <div className="flex items-center gap-2 text-white font-bold font-heading">
            <Radio className="w-5 h-5 text-emerald-400" /> Telemetry & Observability
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-300">Enable Real-Time Telemetry</span>
              <input
                type="checkbox"
                checked={telemetryEnabled}
                onChange={(e) => setTelemetryEnabled(e.target.checked)}
                className="w-4 h-4 text-indigo-600 rounded"
              />
            </div>
            <div className="flex items-center justify-between pt-2">
              <span className="text-sm text-slate-300">Dark Theme Theme Engine</span>
              <span className="text-xs font-mono text-emerald-400">ACTIVE (Glassmorphism)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
