'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function ClusterDashboardPage() {
  const [cluster, setCluster] = useState<any>({
    cluster_name: 'aegisswarm-cluster-main',
    total_workers: 4,
    online_workers: 4,
    total_capacity: 40,
    active_executions: 8,
    queued_tasks: 2,
    workers: [
      { worker_id: 'w-101', hostname: 'node-01', ip_address: '10.0.0.1', cpu_cores: 16, memory_gb: 32, current_load: 3, maximum_capacity: 10, status: 'ONLINE', gpu_available: true },
      { worker_id: 'w-102', hostname: 'node-02', ip_address: '10.0.0.2', cpu_cores: 16, memory_gb: 32, current_load: 2, maximum_capacity: 10, status: 'ONLINE', gpu_available: true },
      { worker_id: 'w-103', hostname: 'node-03', ip_address: '10.0.0.3', cpu_cores: 8, memory_gb: 16, current_load: 2, maximum_capacity: 10, status: 'ONLINE', gpu_available: false },
      { worker_id: 'w-104', hostname: 'node-04', ip_address: '10.0.0.4', cpu_cores: 8, memory_gb: 16, current_load: 1, maximum_capacity: 10, status: 'ONLINE', gpu_available: false }
    ]
  });

  return (
    <div className="p-8 space-y-6 text-slate-100 bg-slate-950 min-h-screen">
      <div className="flex justify-between items-center border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Distributed Worker Cluster Command Center</h1>
          <p className="text-slate-400 text-sm">
            Horizontal scaling, worker heartbeats, load balancing, and fault tolerance control plane.
          </p>
        </div>
        <div className="flex space-x-3">
          <button className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-medium text-xs">
            + Register Worker Node
          </button>
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-medium text-xs">
            Rebalance Cluster
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Cluster Status</p>
          <p className="text-2xl font-bold text-emerald-400 mt-1 uppercase">HEALTHY</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Total / Online Workers</p>
          <p className="text-2xl font-bold text-cyan-400 mt-1">{cluster.online_workers} / {cluster.total_workers}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Cluster Load / Capacity</p>
          <p className="text-2xl font-bold text-purple-400 mt-1">{cluster.active_executions} / {cluster.total_capacity} Slots</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg">
          <p className="text-xs text-slate-400 font-semibold uppercase">Queued Tasks</p>
          <p className="text-2xl font-bold text-amber-400 mt-1">{cluster.queued_tasks} Tasks</p>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 p-5 rounded-lg space-y-4">
        <h3 className="font-semibold text-cyan-400 border-b border-slate-800 pb-2">Active Worker Nodes</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase font-mono border-b border-slate-800">
              <tr>
                <th className="p-3">Worker ID</th>
                <th className="p-3">Hostname</th>
                <th className="p-3">IP Address</th>
                <th className="p-3">CPU / RAM</th>
                <th className="p-3">GPU</th>
                <th className="p-3">Load / Capacity</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 font-mono">
              {cluster.workers.map((w: any) => (
                <tr key={w.worker_id} className="hover:bg-slate-950/50">
                  <td className="p-3 font-semibold text-cyan-400">{w.worker_id}</td>
                  <td className="p-3 text-slate-200">{w.hostname}</td>
                  <td className="p-3 text-slate-400">{w.ip_address}</td>
                  <td className="p-3 text-slate-300">{w.cpu_cores} Cores / {w.memory_gb} GB</td>
                  <td className="p-3">{w.gpu_available ? <span className="text-emerald-400">ENABLED</span> : <span className="text-slate-500">N/A</span>}</td>
                  <td className="p-3 text-purple-300">{w.current_load} / {w.maximum_capacity}</td>
                  <td className="p-3">
                    <span className="bg-emerald-950 text-emerald-400 px-2 py-0.5 rounded text-[10px] border border-emerald-800">
                      {w.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
