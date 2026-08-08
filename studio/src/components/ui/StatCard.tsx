import * as React from "react";
import { LucideIcon } from "lucide-react";
import { Card } from "./Card";
import { cn } from "@/lib/utils";

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
  icon?: LucideIcon;
  description?: string;
  className?: string;
}

export function StatCard({
  title,
  value,
  change,
  trend = "neutral",
  icon: Icon,
  description,
  className,
}: StatCardProps) {
  return (
    <Card className={cn("relative overflow-hidden group", className)}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400 font-mono">
          {title}
        </span>
        {Icon && (
          <div className="p-2 rounded-lg bg-slate-800/80 text-indigo-400 group-hover:text-indigo-300 transition-colors">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold font-mono tracking-tight text-white">
          {value}
        </span>
        {change && (
          <span
            className={cn(
              "text-xs font-semibold font-mono",
              trend === "up" && "text-emerald-400",
              trend === "down" && "text-rose-400",
              trend === "neutral" && "text-slate-400"
            )}
          >
            {change}
          </span>
        )}
      </div>

      {description && (
        <p className="mt-2 text-xs text-slate-400">{description}</p>
      )}
    </Card>
  );
}
