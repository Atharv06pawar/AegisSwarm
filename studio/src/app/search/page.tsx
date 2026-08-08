"use client";

import * as React from "react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { LoadingSpinner } from "@/components/ui/LoadingSpinner";
import { EmptyState } from "@/components/ui/EmptyState";
import { useSearch } from "@/hooks";
import { Search as SearchIcon, Inbox } from "lucide-react";

export default function SearchPage() {
  const searchMutation = useSearch();

  const [queryText, setQueryText] = React.useState("");
  const [taxonomyNode, setTaxonomyNode] = React.useState("");
  const [dataset, setDataset] = React.useState("");
  const [targetModel, setTargetModel] = React.useState("");
  const [attackSuccess, setAttackSuccess] = React.useState<string>("");

  const handleSearch = () => {
    searchMutation.mutate({
      query: queryText || undefined,
      taxonomy_node: taxonomyNode || undefined,
      dataset: dataset || undefined,
      target_model: targetModel || undefined,
      attack_success: attackSuccess === "true" ? true : attackSuccess === "false" ? false : undefined,
      limit: 20,
    });
  };

  const resultsData = searchMutation.data;
  const resultsList = resultsData?.results || [];

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Streaming Search Engine"
        description="Filter and query AttackRecord instances across taxonomy nodes, keywords, target models, and vector payloads."
      />

      <Card className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <SearchIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search prompt payload text, tool calls, or validation messages..."
              className="w-full rounded-lg border border-slate-800 bg-slate-950/80 py-2 pl-9 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none font-sans"
            />
          </div>

          <button
            onClick={handleSearch}
            disabled={searchMutation.isPending}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-2 text-xs font-semibold text-white shadow-md hover:bg-indigo-500 font-sans disabled:opacity-50"
          >
            <SearchIcon className="w-3.5 h-3.5" />
            {searchMutation.isPending ? "Searching..." : "Search Data Lake"}
          </button>
        </div>

        {/* Filter Controls */}
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 pt-2 border-t border-slate-800/80 text-xs font-mono">
          <div>
            <label className="block text-slate-400 mb-1 font-sans">Taxonomy Node</label>
            <input
              type="text"
              value={taxonomyNode}
              onChange={(e) => setTaxonomyNode(e.target.value)}
              placeholder="e.g. AUAO-PI-DIR-RO"
              className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2 text-slate-300 font-mono focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-sans">Dataset Source</label>
            <input
              type="text"
              value={dataset}
              onChange={(e) => setDataset(e.target.value)}
              placeholder="e.g. hackaprompt"
              className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2 text-slate-300 font-mono focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-sans">Target Model</label>
            <input
              type="text"
              value={targetModel}
              onChange={(e) => setTargetModel(e.target.value)}
              placeholder="e.g. gpt-4o"
              className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2 text-slate-300 font-mono focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-slate-400 mb-1 font-sans">Attack Success</label>
            <select
              value={attackSuccess}
              onChange={(e) => setAttackSuccess(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950 p-2 text-slate-300 font-mono focus:border-indigo-500 focus:outline-none"
            >
              <option value="">Any Result</option>
              <option value="true">Success (True)</option>
              <option value="false">Refused (False)</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Query Results */}
      <Card className="space-y-4">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400">
          <span>Query Results: <strong className="text-white">{resultsData?.total_matches ?? resultsList.length} Records Matched</strong></span>
          <span>Execution Time: <strong className="text-indigo-400">{resultsData?.execution_time_ms ?? 0} ms</strong></span>
        </div>

        {resultsList.length > 0 ? (
          <div className="space-y-3 font-mono text-xs">
            {resultsList.map((item: any, idx: number) => (
              <div key={item.sample_id || idx} className="p-3.5 rounded-lg border border-slate-800 bg-slate-950/70 space-y-2 hover:border-indigo-500/40">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="default" className="font-mono">{item.taxonomy_node}</Badge>
                    <span className="text-slate-400 font-mono">source={item.dataset}</span>
                  </div>
                  <Badge variant={item.attack_success ? "danger" : "success"} className="font-mono">
                    {item.attack_success ? "Attack Succeeded" : "Refused"}
                  </Badge>
                </div>

                <p className="text-slate-200 bg-slate-900/60 p-2.5 rounded border border-slate-800/80 font-mono">
                  {item.prompt_sample}
                </p>

                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span>Sample ID: {item.sample_id || "N/A"}</span>
                  <span>Target Model: <strong className="text-slate-300 font-mono">{item.target_model || "N/A"}</strong></span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={Inbox}
            title={searchMutation.isIdle ? "Ready to Search" : "No Matching Records"}
            description={
              searchMutation.isIdle
                ? "Enter keywords or select filter parameters above to execute a Data Lake query."
                : "No AttackRecord instances matched your search criteria."
            }
          />
        )}
      </Card>
    </div>
  );
}
