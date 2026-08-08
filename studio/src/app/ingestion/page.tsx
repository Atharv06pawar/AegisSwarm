"use client";

import * as React from "react";
import { SectionHeader } from "@/components/ui/SectionHeader";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { useJobs } from "@/hooks";
import { PlayCircle, Clock, Terminal } from "lucide-react";

export default function IngestionPage() {
  const { data: jobsData, submitIngest, isSubmitting } = useJobs();
  const [selectedPlugins, setSelectedPlugins] = React.useState<string[]>(["hackaprompt", "agentdojo"]);
  const [dryRun, setDryRun] = React.useState(true);

  const jobsList = jobsData?.jobs || [];

  const handleTogglePlugin = (pluginId: string) => {
    setSelectedPlugins((prev) =>
      prev.includes(pluginId) ? prev.filter((p) => p !== pluginId) : [...prev, pluginId]
    );
  };

  const handleSubmit = async () => {
    if (selectedPlugins.length === 0) return;
    await submitIngest({ datasets: selectedPlugins, dry_run: dryRun, batch_size: 1000 });
  };

  return (
    <div className="space-y-6">
      <SectionHeader
        title="Streaming Ingestion Pipeline"
        description="Launch non-blocking streaming ingestion jobs over benchmark plugins using PipelineOrchestrator."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Launch New Job Form */}
        <Card className="space-y-4">
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <Terminal className="w-4 h-4 text-indigo-400" />
            Submit Ingestion Task
          </h3>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-400 font-mono mb-1">Target Plugins</label>
              <div className="space-y-1.5 border border-slate-800 rounded-lg p-2.5 bg-slate-950/50">
                {["hackaprompt", "agentdojo", "pyrit", "garak", "advbench"].map((item) => (
                  <label key={item} className="flex items-center gap-2 text-slate-300 font-mono cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedPlugins.includes(item)}
                      onChange={() => handleTogglePlugin(item)}
                      className="rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-0"
                    />
                    <span className="capitalize">{item}</span>
                  </label>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-slate-400 font-mono mb-1">Batch Size</label>
              <input
                type="number"
                defaultValue={1000}
                className="w-full rounded-lg border border-slate-800 bg-slate-950/50 p-2 text-slate-200 font-mono focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <label className="flex items-center gap-2 text-slate-300 font-mono pt-1 cursor-pointer">
              <input
                type="checkbox"
                checked={dryRun}
                onChange={(e) => setDryRun(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-0"
              />
              <span>Dry Run Mode (No Lake Writes)</span>
            </label>

            <button
              onClick={handleSubmit}
              disabled={isSubmitting || selectedPlugins.length === 0}
              className="w-full mt-2 inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 py-2.5 font-semibold text-white shadow-md shadow-indigo-600/20 hover:bg-indigo-500 transition-colors font-sans disabled:opacity-50"
            >
              <PlayCircle className="w-4 h-4" />
              {isSubmitting ? "Submitting Job..." : "Start Background Ingestion"}
            </button>
          </div>
        </Card>

        {/* Jobs History Table */}
        <Card className="lg:col-span-2 space-y-4">
          <h3 className="text-base font-bold text-white font-heading flex items-center gap-2">
            <Clock className="w-4 h-4 text-cyan-400" />
            Background Ingestion Jobs
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="border-b border-slate-800 text-slate-400">
                <tr>
                  <th className="pb-3 font-semibold">Job ID</th>
                  <th className="pb-3 font-semibold">Status</th>
                  <th className="pb-3 font-semibold">Progress</th>
                  <th className="pb-3 font-semibold">Records</th>
                  <th className="pb-3 font-semibold">Elapsed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {jobsList.map((job: any) => (
                  <tr key={job.job_id} className="hover:bg-slate-800/40">
                    <td className="py-3 font-bold text-white">{job.job_id}</td>
                    <td className="py-3">
                      <Badge variant={job.status === "completed" ? "success" : job.status === "failed" ? "danger" : "warning"}>
                        {job.status}
                      </Badge>
                    </td>
                    <td className="py-3">
                      <div className="w-24 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full" style={{ width: `${job.progress_percentage}%` }} />
                      </div>
                    </td>
                    <td className="py-3">{job.records_processed} recs</td>
                    <td className="py-3 text-slate-400">{job.elapsed_seconds}s</td>
                  </tr>
                ))}
                {jobsList.length === 0 && (
                  <tr>
                    <td colSpan={5} className="py-6 text-center text-slate-500 font-sans">
                      No ingestion jobs executed yet. Submit a task above to begin.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
