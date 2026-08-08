"use client";

import * as React from "react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { StatCard } from "@/components/ui/StatCard";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useDashboard } from "@/hooks";
import { formatBytes } from "@/lib/utils";
import {
  Database,
  Layers,
  ShieldAlert,
  CheckCircle2,
  TrendingUp,
  Activity,
  ArrowRight,
  Terminal,
  Inbox
} from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { data: dashboard, isLoading, isError } = useDashboard();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <LoadingSpinner size="lg" />
        <span className="text-xs font-mono text-slate-400">Loading Data Lake telemetry...</span>
      </div>
    );
  }

  const totalRecords = (dashboard?.total_records ?? 0).toLocaleString();
  const totalDatasets = dashboard?.total_datasets ?? 0;
  const totalSize = formatBytes(dashboard?.total_size_bytes ?? 0);
  const coveragePct = `${dashboard?.ontology_coverage ?? 0}%`;
  const verificationStatus = dashboard?.verification_status || "N/A";

  const rootClassDist: Record<string, number> = dashboard?.root_class_distribution || {};
  const activePlugins: string[] = dashboard?.active_plugins || [];

  return (
    <div className="space-y-6">
      <SectionHeader
        title="AI Red Teaming Command Center"
        description="Real-time monitoring of AegisSwarm Universal Attack Ontology (AUAO v1.0) streaming pipeline."
        action={
          <Link
            href="/ingestion"
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-500 transition-colors font-sans"
          >
            <Terminal className="w-3.5 h-3.5" />
            Launch Ingestion
          </Link>
        }
      />

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Ingested Records"
          value={totalRecords}
          icon={Database}
          description={`Footprint: ${totalSize}`}
        />
        <StatCard
          title="Registered Datasets"
          value={`${totalDatasets} Suites`}
          icon={Layers}
          description="Active benchmark dataset plugins"
        />
        <StatCard
          title="AUAO Coverage"
          value={coveragePct}
          icon={ShieldAlert}
          description="Ontology tree node representation"
        />
        <StatCard
          title="Data Lake Health"
          value={verificationStatus}
          icon={CheckCircle2}
          description="Cryptographic SHA256 status"
        />
      </div>

      {/* Secondary Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Benchmark Datasets */}
        <Card className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
              <Activity className="w-4 h-4 text-indigo-400" />
              Active Benchmark Datasets
            </h3>
            <Link href="/plugins" className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-sans">
              View All <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {activePlugins.length > 0 ? (
            <div className="divide-y divide-slate-800">
              {activePlugins.map((plugName: string, idx: number) => (
                <div key={idx} className="py-3 flex items-center justify-between text-xs">
                  <div className="space-y-0.5">
                    <div className="font-bold text-white font-heading text-sm flex items-center gap-2 capitalize">
                      {plugName}
                      <Badge variant="default" className="text-[10px] py-0 font-mono">AUAO-REGISTERED</Badge>
                    </div>
                    <div className="text-slate-400 font-sans">Dataset Plugin</div>
                  </div>
                  <div className="text-right font-mono">
                    <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 font-sans">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Loaded
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={Inbox}
              title="No Installed Datasets"
              description="The Data Lake currently contains no ingested partitions. Submit an ingestion task to populate the lake."
              action={
                <Link
                  href="/ingestion"
                  className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 transition-colors font-sans"
                >
                  <Terminal className="w-3.5 h-3.5" />
                  Run First Ingestion
                </Link>
              }
            />
          )}
        </Card>

        {/* Ontology Quick Summary */}
        <Card className="space-y-4">
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            AUAO Root Class Distribution
          </h3>
          <p className="text-xs text-slate-400 font-sans">
            Represented attack domains across data lake partitions.
          </p>

          {Object.keys(rootClassDist).length > 0 ? (
            <div className="space-y-3 pt-2">
              {Object.entries(rootClassDist).map(([key, rawCount]: [string, number], idx: number) => {
                const valCount = Number(rawCount) || 0;
                const totalSum = Object.values(rootClassDist).reduce((a: number, b: number) => a + Number(b), 0) || 1;
                const pct = Math.round((valCount / totalSum) * 100);
                const colors = ["bg-indigo-500", "bg-cyan-500", "bg-emerald-500", "bg-amber-500", "bg-rose-500"];
                return (
                  <div key={idx} className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-slate-300 font-sans">{key}</span>
                      <span className="text-slate-400 font-mono font-semibold">{pct}%</span>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${colors[idx % colors.length]}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState
              icon={TrendingUp}
              title="No Mapped Taxonomies"
              description="Root class distribution metrics will populate once datasets are ingested."
            />
          )}
        </Card>
      </div>
    </div>
  );
}
