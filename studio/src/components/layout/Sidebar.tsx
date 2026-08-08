"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Plug,
  Database,
  GitMerge,
  Search,
  FileText,
  Settings,
  PlayCircle,
  Shield,
  X
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Plugins", href: "/plugins", icon: Plug },
  { name: "Ingestion", href: "/ingestion", icon: PlayCircle },
  { name: "Corpus", href: "/corpus", icon: Database },
  { name: "Ontology", href: "/ontology", icon: GitMerge },
  { name: "Search", href: "/search", icon: Search },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-screen w-64 border-r border-slate-800 bg-cyber-bg px-4 py-4 flex flex-col justify-between transition-transform duration-300 ease-in-out lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div>
          {/* Header / Brand Logo */}
          <div className="flex items-center justify-between px-2 pb-6 border-b border-slate-800/80">
            <Link href="/" className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-600/20 border border-indigo-500/40 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]">
                <Shield className="h-5 w-5" />
              </div>
              <div className="flex flex-col">
                <span className="text-lg font-bold tracking-tight text-white font-heading leading-none">
                  AegisSwarm
                </span>
                <span className="text-[10px] font-semibold tracking-widest text-indigo-400 uppercase font-mono mt-1">
                  Studio v2.0
                </span>
              </div>
            </Link>
            <button
              onClick={onClose}
              className="p-1 rounded-md text-slate-400 hover:text-white lg:hidden"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation Links */}
          <nav className="mt-6 space-y-1">
            {navItems.map((item) => {
              const isActive =
                item.href === "/"
                  ? pathname === "/"
                  : pathname.startsWith(item.href);

              const Icon = item.icon;

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all font-sans",
                    isActive
                      ? "bg-indigo-600/15 text-indigo-300 border border-indigo-500/30 shadow-sm"
                      : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                  )}
                >
                  <Icon
                    className={cn(
                      "h-4 w-4 transition-colors",
                      isActive ? "text-indigo-400" : "text-slate-400"
                    )}
                  />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer info */}
        <div className="pt-4 border-t border-slate-800/80 px-2">
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
              <span>AUAO Framework</span>
              <span className="text-emerald-400 font-semibold font-mono">v1.0</span>
            </div>
            <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400 font-sans">
              <span>Status</span>
              <span className="flex items-center gap-1 text-emerald-400 font-medium font-mono">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Operational
              </span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
