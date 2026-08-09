"use client";

import React, { useState } from "react";
import { Play, Check, ChevronRight, Zap, Shield, Database, Cpu } from "lucide-react";

export default function BenchmarkWizardPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);

  const steps = [
    "Choose Datasets",
    "Choose Providers",
    "Choose Attack Agents",
    "Choose Mutation Families",
    "Budget Control",
    "Parallel Workers",
    "Review",
    "Run Experiment"
  ];

  const handleLaunch = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/experiments/benchmark/launch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          objective: "Studio Benchmark Wizard Experiment Execution",
          max_attacks_per_dataset: 5,
          parallelism: 4
        })
      });
      if (res.ok) {
        setReport(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-[1400px] mx-auto">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4">
        <h1 className="text-2xl font-bold text-white font-heading">Benchmark Wizard</h1>
        <p className="text-slate-400 text-sm mt-1">Configure and Launch Autonomous AI Red-Teaming Experiments</p>
      </div>

      {/* Step Indicator */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-2">
        {steps.map((s, idx) => {
          const num = idx + 1;
          const active = step === num;
          const done = step > num;
          return (
            <button
              key={s}
              onClick={() => setStep(num)}
              className={`p-3 rounded-lg border text-left text-xs font-mono transition ${
                active
                  ? "bg-indigo-600 border-indigo-500 text-white font-bold"
                  : done
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                  : "bg-slate-900 border-slate-800 text-slate-400"
              }`}
            >
              <div className="text-[10px] opacity-75">STEP {num}</div>
              <div className="truncate mt-0.5">{s}</div>
            </button>
          );
        })}
      </div>

      {/* Wizard Content Panel */}
      <div className="p-8 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-6 min-h-[300px]">
        <h2 className="text-xl font-bold text-white font-heading">{steps[step - 1]}</h2>

        {step === 1 && (
          <div className="space-y-2 text-sm text-slate-300">
            <div className="p-3 rounded bg-slate-800/40 border border-slate-800">✓ HackAPrompt (10 records)</div>
            <div className="p-3 rounded bg-slate-800/40 border border-slate-800">✓ AgentDojo (2 records)</div>
            <div className="p-3 rounded bg-slate-800/40 border border-slate-800">✓ Garak Vulnerabilities (2 records)</div>
            <div className="p-3 rounded bg-slate-800/40 border border-slate-800">✓ PyRIT Red-Team (2 records)</div>
            <div className="p-3 rounded bg-slate-800/40 border border-slate-800">✓ PromptInject (2 records)</div>
            <div className="p-3 rounded bg-slate-800/40 border border-slate-800">✓ JailbreakBench (2 records)</div>
            <div className="p-3 rounded bg-slate-800/40 border border-slate-800">✓ AdvBench (2 records)</div>
          </div>
        )}

        {step === 8 && (
          <div className="space-y-4 text-center py-6">
            <button
              onClick={handleLaunch}
              disabled={loading}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-base shadow-lg transition flex items-center gap-2 mx-auto"
            >
              <Play className="w-5 h-5" />
              {loading ? "Executing Experiment..." : "Launch Research Benchmark Harness"}
            </button>

            {report && (
              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm font-mono mt-4">
                ✓ Benchmark Execution Complete! Benchmark ID: {report.benchmark_id} (Status: {report.overall_health})
              </div>
            )}
          </div>
        )}

        {/* Wizard Controls */}
        <div className="flex justify-between pt-4 border-t border-slate-800">
          <button
            disabled={step === 1}
            onClick={() => setStep(step - 1)}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm disabled:opacity-50"
          >
            Back
          </button>
          <button
            disabled={step === 8}
            onClick={() => setStep(step + 1)}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm flex items-center gap-1"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
