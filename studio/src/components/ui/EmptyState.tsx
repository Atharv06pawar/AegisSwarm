import * as React from "react";
import { LucideIcon, Inbox } from "lucide-react";
import { cn } from "@/lib/utils";

export interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-12 text-center rounded-xl border border-dashed border-slate-800 bg-slate-900/40",
        className
      )}
    >
      <div className="p-4 rounded-full bg-slate-800/60 text-slate-400 mb-4 border border-slate-700/50">
        <Icon className="w-8 h-8 text-indigo-400" />
      </div>
      <h3 className="text-base font-semibold text-white font-sans">{title}</h3>
      <p className="mt-1 text-sm text-slate-400 max-w-sm">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
