"use client";

import React, { useState, useEffect } from "react";
import { FileText, Download, Eye, RefreshCw, CheckCircle, FileCode } from "lucide-react";

export default function ReportCenterPage() {
  const [reports, setReports] = useState<Record<string, string>>({});
  const [selectedReport, setSelectedReport] = useState<string | null>(null);
  const [reportContent, setReportContent] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/research/reports");
      if (res.ok) {
        const data = await res.json();
        setReports(data.reports || {});
        if (Object.keys(data.reports || {}).length > 0) {
          const firstKey = Object.keys(data.reports)[0];
          setSelectedReport(firstKey);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="border-b border-slate-800 pb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-heading">Report Center & Scientific Publication Hub</h1>
          <p className="text-slate-400 text-sm mt-1">Browse, Preview, and Export All 16 Scientific Markdown & JSON Reports</p>
        </div>
        <button
          onClick={fetchReports}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-slate-800 text-slate-200 rounded-lg text-sm border border-slate-700 hover:bg-slate-700 transition"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /> Refresh Reports
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar File Listing */}
        <div className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-2">
          <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-2">
            AVAILABLE PUBLICATION REPORTS ({Object.keys(reports).length})
          </div>
          {Object.keys(reports).map((fname) => (
            <button
              key={fname}
              onClick={() => setSelectedReport(fname)}
              className={`w-full text-left p-2.5 rounded-lg text-xs font-mono transition flex items-center gap-2 ${
                selectedReport === fname
                  ? "bg-indigo-600 text-white font-bold"
                  : "text-slate-300 hover:bg-slate-800"
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span className="truncate">{fname}</span>
            </button>
          ))}
        </div>

        {/* Right Preview Panel */}
        <div className="lg:col-span-3 p-6 rounded-xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm space-y-4 min-h-[500px]">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <span className="font-bold text-white font-mono text-sm">
              {selectedReport || "No Report Selected"}
            </span>
            {selectedReport && (
              <a
                href={`/api/v1/research/reports`}
                download
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium font-mono"
              >
                <Download className="w-3.5 h-3.5" /> Download Report
              </a>
            )}
          </div>
          <div className="p-4 rounded bg-slate-950 border border-slate-850 font-mono text-xs text-slate-200 leading-relaxed overflow-x-auto whitespace-pre-wrap">
            {selectedReport
              ? `# Scientific Publication Report Preview: ${selectedReport}\n\nGenerated automatically by AegisSwarm Research Subsystem.`
              : "Select a report from the list to preview content."}
          </div>
        </div>
      </div>
    </div>
  );
}
