"use client";

import * as React from "react";
import { Menu, Search, Activity, Cpu } from "lucide-react";
import { Badge } from "@/components/ui/Badge";

interface NavbarProps {
  onMenuClick: () => void;
}

export function Navbar({ onMenuClick }: NavbarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-800 bg-cyber-bg/90 px-4 sm:px-6 backdrop-blur-md">
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="p-2 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Global Search Bar */}
        <div className="relative hidden md:block w-72">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search AUAO nodes, datasets, prompts..."
            className="w-full rounded-lg border border-slate-800 bg-slate-900/80 py-1.5 pl-9 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:border-indigo-500/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/50 font-sans"
          />
        </div>
      </div>

      {/* Top Bar Actions & Status */}
      <div className="flex items-center gap-3">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full border border-slate-800 bg-slate-900/60 text-xs text-slate-400 font-mono">
          <Activity className="h-3.5 w-3.5 text-emerald-400 animate-pulse" />
          <span>Data Lake Status:</span>
          <span className="text-emerald-400 font-semibold">HEALTHY</span>
        </div>

        <Badge variant="neon" className="hidden md:inline-flex gap-1.5">
          <Cpu className="h-3 w-3 text-cyan-400" />
          AUAO v1.0 Standard
        </Badge>
      </div>
    </header>
  );
}
