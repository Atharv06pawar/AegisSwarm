import * as React from "react";
import { cn } from "@/lib/utils";

export interface SectionHeaderProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function SectionHeader({
  title,
  description,
  action,
  className,
}: SectionHeaderProps) {
  return (
    <div className={cn("flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800", className)}>
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white font-heading flex items-center gap-2">
          {title}
        </h1>
        {description && (
          <p className="mt-1 text-sm text-slate-400 font-sans">{description}</p>
        )}
      </div>
      {action && <div className="flex items-center gap-3">{action}</div>}
    </div>
  );
}
