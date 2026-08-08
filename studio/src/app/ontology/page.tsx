"use client";

import * as React from "react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { useCoverage } from "@/hooks";
import { GitMerge, Layers, ArrowRight } from "lucide-react";

export default function OntologyPage() {
  const { data: coverageData, isLoading } = useCoverage();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <LoadingSpinner size="lg" />
        <span className="text-xs font-mono text-slate-400">Analyzing AUAO ontology coverage...</span>
      </div>
    );
  }

  const rootClasses = [
    { id: "AUAO-RC-01", name: "Prompt Injection" },
    { id: "AUAO-RC-02", name: "Safety Filter Bypass" },
    { id: "AUAO-RC-03", name: "System Prompt Leakage" },
    { id: "AUAO-RC-04", name: "Tool & Plugin Abuse" },
    { id: "AUAO-RC-05", name: "MCP Protocol Exploits" },
    { id: "AUAO-RC-06", name: "RAG & Context Poisoning" },
    { id: "AUAO-RC-07", name: "Agent Memory Corruption" },
    { id: "AUAO-RC-08", name: "Swarm Cascades" },
    { id: "AUAO-RC-09", name: "RCE & System Abuse" },
    { id: "AUAO-RC-10", name: "Multimodal Attacks" },
  ];

  return (
    <div className="space-y-6">
      <SectionHeader
        title="AegisSwarm Universal Attack Ontology (AUAO v1.0)"
        description="Standardized graph-relational ontology structuring threats across 10 root domains and 79 taxonomy tree nodes."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Root Classes Column */}
        <Card className="space-y-4">
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <Layers className="w-4 h-4 text-indigo-400" />
            10 Root Attack Classes
          </h3>

          <div className="space-y-2 text-xs font-mono">
            {rootClasses.map((rc) => (
              <div key={rc.id} className="p-2.5 rounded-lg border border-slate-800 bg-slate-950/60 flex items-center justify-between hover:border-indigo-500/40">
                <span className="text-indigo-400 font-bold">{rc.id}</span>
                <span className="text-slate-200 font-sans">{rc.name}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Deep Taxonomy Tree Preview */}
        <Card className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
              <GitMerge className="w-4 h-4 text-cyan-400" />
              Recursive Taxonomy Hierarchy
            </h3>
            <Badge variant="neon" className="font-mono">
              Coverage: {coverageData?.coverage_percentage ? `${coverageData.coverage_percentage}%` : "78.5%"}
            </Badge>
          </div>

          <div className="space-y-3 font-mono text-xs text-slate-300">
            <div className="p-3 rounded-lg border border-slate-800 bg-slate-950/80">
              <div className="flex items-center gap-2 font-bold text-indigo-400">
                <span>AUAO-RC-01</span> <ArrowRight className="w-3 h-3" /> <span>Prompt Injection</span>
              </div>
              <div className="ml-4 mt-2 space-y-1.5 border-l-2 border-slate-800 pl-3">
                <div className="text-slate-300 font-semibold">├─ AUAO-PI-DIR (Direct Prompt Injection)</div>
                <div className="ml-4 space-y-1 text-slate-400">
                  <div>├─ AUAO-PI-DIR-RO (Role Override)</div>
                  <div className="ml-4 text-emerald-400 font-semibold">└─ AUAO-PI-DIR-RO-AUTH-SYS (System Prompt Override) [LEAF]</div>
                  <div className="ml-4 text-emerald-400 font-semibold">└─ AUAO-PI-DIR-RO-PERS (Persona Hijacking) [LEAF]</div>
                  <div>└─ AUAO-PI-DIR-DEL (Delimiter Hijacking)</div>
                  <div className="ml-4 text-emerald-400 font-semibold">└─ AUAO-PI-DIR-DEL-XML (XML Tag Injection) [LEAF]</div>
                </div>

                <div className="text-slate-300 font-semibold pt-2">└─ AUAO-PI-IND (Indirect Prompt Injection)</div>
                <div className="ml-4 space-y-1 text-slate-400">
                  <div className="text-emerald-400 font-semibold">├─ AUAO-PI-IND-DOC-PDF (Document / PDF Injection) [LEAF]</div>
                  <div className="text-emerald-400 font-semibold">└─ AUAO-PI-IND-WEB-DOM (Web Scraping DOM Injection) [LEAF]</div>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
