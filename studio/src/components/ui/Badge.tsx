import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "success" | "warning" | "danger" | "neon";
}

export function Badge({
  className,
  variant = "default",
  ...props
}: BadgeProps) {
  const variants = {
    default: "bg-indigo-950/70 text-indigo-300 border-indigo-800/50",
    secondary: "bg-slate-800 text-slate-300 border-slate-700",
    outline: "bg-transparent text-slate-300 border-slate-700",
    success: "bg-emerald-950/70 text-emerald-300 border-emerald-800/50",
    warning: "bg-amber-950/70 text-amber-300 border-amber-800/50",
    danger: "bg-rose-950/70 text-rose-300 border-rose-800/50",
    neon: "bg-cyan-950/70 text-cyan-300 border-cyan-800/50 shadow-[0_0_10px_rgba(6,182,212,0.3)]",
  };

  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold font-mono transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
        variants[variant],
        className
      )}
      {...props}
    />
  );
}
