"use client";

import * as React from "react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { usePlugins } from "@/hooks";
import { Plug, RefreshCw, ExternalLink, CheckCircle2, Inbox } from "lucide-react";

export default function PluginsPage() {
  const { data: pluginsData, isLoading, discover, isDiscovering } = usePlugins();

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] space-y-4">
        <LoadingSpinner size="lg" />
        <span className="text-xs font-mono text-slate-400">Discovering dataset plugins...</span>
      </div>
    );
  }

  const pluginsList = pluginsData?.plugins || [];

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Dataset Ingestion Plugins"
        description="Registered BaseDatasetPlugin subclasses auto-discovered by the AegisSwarm engine."
        action={
          <button
            onClick={() => discover()}
            disabled={isDiscovering}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-700 hover:text-white transition-colors font-sans disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isDiscovering ? "animate-spin" : ""}`} />
            {isDiscovering ? "Discovering..." : "Discover Plugins"}
          </button>
        }
      />

      {pluginsList.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {pluginsList.map((plugin: any) => (
            <Card key={plugin.dataset_id} className="flex flex-col justify-between space-y-4 hover:border-indigo-500/40">
              <div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-indigo-950/60 border border-indigo-800/40 text-indigo-400">
                      <Plug className="w-4 h-4" />
                    </div>
                    <h3 className="text-lg font-bold text-white font-heading capitalize">{plugin.dataset_id}</h3>
                  </div>
                  <Badge variant="success" className="gap-1 font-mono">
                    <CheckCircle2 className="w-3 h-3" />
                    Registered
                  </Badge>
                </div>

                <p className="mt-3 text-xs text-slate-300 font-sans leading-relaxed">
                  {plugin.description || "No description provided."}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800 space-y-2 text-xs">
                <div className="flex items-center justify-between text-slate-400 font-sans">
                  <span>Parser Version:</span>
                  <Badge variant="default" className="font-mono">v{plugin.parser_version}</Badge>
                </div>

                <div className="flex items-center justify-between text-slate-400 font-sans">
                  <span>License:</span>
                  <span className="text-slate-200 font-semibold font-mono">{plugin.license_name}</span>
                </div>

                {plugin.license_url && (
                  <a
                    href={plugin.license_url}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-2 inline-flex items-center gap-1 text-[11px] text-indigo-400 hover:text-indigo-300 font-sans"
                  >
                    <span>Repository Reference</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Inbox}
          title="No Dataset Plugins Registered"
          description="Click 'Discover Plugins' above to scan the dataset directory and register plugins."
          action={
            <button
              onClick={() => discover()}
              className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 transition-colors font-sans"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Discover Plugins
            </button>
          }
        />
      )}
    </div>
  );
}
