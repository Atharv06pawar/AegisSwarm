"use client";

import * as React from "react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useReports } from "@/hooks";
import { formatBytes } from "@/lib/utils";
import { FileText, Download, FileCode, Inbox } from "lucide-react";

export default function ReportsPage() {
  const { data: reportsData, isLoading, generateReports, isGenerating } = useReports();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <LoadingSpinner size="lg" />
        <span className="text-xs font-mono text-slate-400">Fetching publication report status...</span>
      </div>
    );
  }

  const reportsList = reportsData?.reports || [];

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Publication Research Reports"
        description="Generate and export publication-grade Markdown research whitepapers and structured JSON reports."
        action={
          <button
            onClick={() => generateReports()}
            disabled={isGenerating}
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 transition-colors font-sans disabled:opacity-50"
          >
            <Download className={`w-3.5 h-3.5 ${isGenerating ? "animate-spin" : ""}`} />
            {isGenerating ? "Generating Reports..." : "Export Latest Whitepaper"}
          </button>
        }
      />

      {reportsList.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {reportsList.map((rpt: any) => (
            <Card key={rpt.filename} className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {rpt.format === "markdown" ? (
                    <FileText className="w-5 h-5 text-indigo-400" />
                  ) : (
                    <FileCode className="w-5 h-5 text-cyan-400" />
                  )}
                  <h3 className="text-lg font-bold text-white font-heading">{rpt.filename}</h3>
                </div>
                <Badge variant={rpt.format === "markdown" ? "success" : "neon"} className="font-mono uppercase">
                  {rpt.format}
                </Badge>
              </div>

              <p className="text-xs text-slate-300 font-sans leading-relaxed">
                {rpt.format === "markdown"
                  ? "Publication-grade GitHub-Flavored Markdown whitepaper outlining Executive Summary, Dataset Inventory, AUAO v1.0 Coverage Analysis, Quality Audit Metrics, and Cryptographic Verification Status."
                  : "Complete structured JSON object serializing primitive counters, AUAO root class distribution matrix, quality audit metrics, and lineage verification records for automated API consumption."}
              </p>

              <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] font-mono text-slate-400 space-y-1">
                <div>Destination: <code>{rpt.file_path}</code></div>
                <div>Size: <code>{formatBytes(rpt.size_bytes || 0)}</code></div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Inbox}
          title="No Reports Generated Yet"
          description="Click 'Export Latest Whitepaper' above to generate corpus_report.md and corpus_report.json."
          action={
            <button
              onClick={() => generateReports()}
              disabled={isGenerating}
              className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 transition-colors font-sans"
            >
              <Download className="w-3.5 h-3.5" />
              Generate Initial Whitepaper
            </button>
          }
        />
      )}
    </div>
  );
}
