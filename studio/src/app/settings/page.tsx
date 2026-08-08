"use client";

import * as React from "react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Card } from "@/components/ui/Card";
import { Settings, Cpu, HardDrive, Terminal } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <SectionHeader
        title="Studio Configuration"
        description="Configure API service endpoints, Data Lake storage paths, and AUAO ontology framework settings."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 font-mono text-xs">
        <Card className="space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" />
            FastAPI Service Connection
          </h3>

          <div className="space-y-3">
            <div>
              <label className="block text-slate-400 mb-1">API Base Endpoint</label>
              <input
                type="text"
                defaultValue="http://127.0.0.1:8000/api/v1"
                className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">CORS Origins Allowed</label>
              <input
                type="text"
                defaultValue="*"
                className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>
        </Card>

        <Card className="space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <HardDrive className="w-4 h-4 text-cyan-400" />
            Data Lake Storage Options
          </h3>

          <div className="space-y-3">
            <div>
              <label className="block text-slate-400 mb-1">Lake Base Path</label>
              <input
                type="text"
                defaultValue="outputs/lake"
                className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1">Lineage Manifest Path</label>
              <input
                type="text"
                defaultValue="outputs/lineage_manifest.json"
                className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2 text-slate-200 focus:border-indigo-500 focus:outline-none"
              />
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
