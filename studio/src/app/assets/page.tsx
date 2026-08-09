"use client";

import React, { useState, useEffect } from "react";
import {
  Cpu,
  Database,
  Shield,
  FileText,
  Plug,
  Plus,
  Trash2,
  CheckCircle,
  Upload,
  RefreshCw
} from "lucide-react";

export default function AssetManagementPage() {
  const [activeTab, setActiveTab] = useState<"providers" | "datasets" | "agents" | "templates" | "plugins">("providers");
  const [providers, setProviders] = useState<any[]>([]);
  const [agents, setAgents] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [plugins, setPlugins] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // New Asset State Forms
  const [newProviderName, setNewProviderName] = useState("");
  const [newAgentName, setNewAgentName] = useState("");

  const fetchData = async () => {
    setLoading(true);
    try {
      const [resP, resA, resT, resPl] = await Promise.all([
        fetch("/api/v1/assets/providers"),
        fetch("/api/v1/assets/agents"),
        fetch("/api/v1/assets/templates"),
        fetch("/api/v1/assets/plugins")
      ]);
      if (resP.ok) setProviders(await resP.json());
      if (resA.ok) setAgents(await resA.json());
      if (resT.ok) setTemplates(await resT.json());
      if (resPl.ok) setPlugins(await resPl.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleAddProvider = async () => {
    if (!newProviderName) return;
    const pid = newProviderName.toLowerCase().replace(/\s+/g, "_");
    await fetch("/api/v1/assets/providers", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider_id: pid,
        name: newProviderName,
        enabled: true,
        model: "custom-v1",
        temperature: 0.7,
        max_tokens: 2048
      })
    });
    setNewProviderName("");
    fetchData();
  };

  const handleAddAgent = async () => {
    if (!newAgentName) return;
    await fetch("/api/v1/assets/agents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        id: `agent_${Date.now()}`,
        name: newAgentName,
        family: "Custom",
        mutation_family: "Persona",
        mode: "Single turn",
        enabled: true
      })
    });
    setNewAgentName("");
    fetchData();
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight font-heading">
            Asset Management Center
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            No-Code Management for Target LLM Providers, Datasets, Attack Agents, Prompt Templates & Plugins
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-200 rounded-lg text-sm font-medium border border-slate-700 hover:bg-slate-700 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab("providers")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "providers" ? "bg-indigo-600 text-white" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          <Cpu className="w-4 h-4" /> Provider Manager
        </button>
        <button
          onClick={() => setActiveTab("datasets")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "datasets" ? "bg-indigo-600 text-white" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          <Database className="w-4 h-4" /> Dataset Manager
        </button>
        <button
          onClick={() => setActiveTab("agents")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "agents" ? "bg-indigo-600 text-white" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          <Shield className="w-4 h-4" /> Attack Agent Builder
        </button>
        <button
          onClick={() => setActiveTab("templates")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "templates" ? "bg-indigo-600 text-white" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          <FileText className="w-4 h-4" /> Prompt Templates
        </button>
        <button
          onClick={() => setActiveTab("plugins")}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition ${
            activeTab === "plugins" ? "bg-indigo-600 text-white" : "text-slate-400 hover:bg-slate-800"
          }`}
        >
          <Plug className="w-4 h-4" /> Plugin Manager
        </button>
      </div>

      {/* PROVIDERS TAB */}
      {activeTab === "providers" && (
        <div className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="New Provider Name..."
              value={newProviderName}
              onChange={(e) => setNewProviderName(e.target.value)}
              className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleAddProvider}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition"
            >
              <Plus className="w-4 h-4" /> Add Provider
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {providers.map((p) => (
              <div key={p.provider_id} className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white font-mono">{p.name}</span>
                  <span className={`px-2 py-0.5 rounded text-xs font-mono ${p.enabled ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-800 text-slate-400"}`}>
                    {p.enabled ? "ACTIVE" : "DISABLED"}
                  </span>
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  Default Model: <span className="text-slate-200">{p.model}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* DATASETS TAB */}
      {activeTab === "datasets" && (
        <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4">
          <h2 className="text-lg font-bold text-white font-heading">Dataset Import & Upload Wizard</h2>
          <div className="border-2 border-dashed border-slate-800 rounded-xl p-8 text-center space-y-3">
            <Upload className="w-8 h-8 text-indigo-400 mx-auto" />
            <div className="text-sm text-slate-300">Drag and drop CSV, JSON, JSONL, Parquet, or ZIP datasets</div>
            <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium">
              Browse Files
            </button>
          </div>
        </div>
      )}

      {/* ATTACK AGENTS TAB */}
      {activeTab === "agents" && (
        <div className="space-y-4">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="New Attack Agent Name..."
              value={newAgentName}
              onChange={(e) => setNewAgentName(e.target.value)}
              className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500"
            />
            <button
              onClick={handleAddAgent}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm font-medium transition"
            >
              <Plus className="w-4 h-4" /> Build Agent
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {agents.map((a) => (
              <div key={a.id} className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-white font-mono">{a.name}</span>
                  <span className="text-xs text-indigo-400 font-mono">{a.mode}</span>
                </div>
                <div className="text-xs text-slate-400 font-mono">
                  Mutation: <span className="text-slate-200">{a.mutation_family}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PROMPT TEMPLATES TAB */}
      {activeTab === "templates" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((t) => (
            <div key={t.id} className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-2">
              <div className="font-bold text-white text-sm font-mono">{t.name}</div>
              <div className="text-xs text-indigo-400 font-mono">{t.family}</div>
              <div className="p-2 rounded bg-slate-950 font-mono text-xs text-slate-300 truncate">
                {t.template}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* PLUGINS TAB */}
      {activeTab === "plugins" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {plugins.map((pl) => (
            <div key={pl.id} className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm flex justify-between items-center">
              <div>
                <div className="font-bold text-white text-sm font-mono">{pl.name}</div>
                <div className="text-xs text-slate-400 font-mono">{pl.type}</div>
              </div>
              <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded text-xs font-mono">
                INSTALLED
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
