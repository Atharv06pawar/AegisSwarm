"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Plug,
  PlayCircle,
  Database,
  GitMerge,
  Search,
  FileText,
  Settings,
  Shield,
  Layers,
  FlaskConical,
  Radio,
  BarChart2,
  X
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Assets Center", href: "/assets", icon: Layers },
  { name: "Benchmark Wizard", href: "/experiments", icon: FlaskConical },
  { name: "Live Control", href: "/live", icon: Radio },
  { name: "Report Hub", href: "/analysis", icon: BarChart2 },
  { name: "Research Platform", href: "/research", icon: Shield },
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
          "fixed top-0 bottom-0 left-0 z-50 w-64 border-r border-slate-800 bg-slate-950/95 backdrop-blur-md transition-transform duration-200 ease-in-out lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Header */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-6">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold font-mono">
              A
            </div>
            <span className="font-bold text-white tracking-wider font-mono">
              Aegis<span className="text-indigo-400">Swarm</span>
            </span>
          </Link>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Nav Items */}
        <div className="px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-xs font-mono transition-colors",
                  isActive
                    ? "bg-indigo-600/20 text-indigo-400 font-semibold border border-indigo-500/30"
                    : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                )}
                onClick={() => {
                  if (window.innerWidth < 1024) onClose();
                }}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </div>
      </aside>
    </>
  );
}
