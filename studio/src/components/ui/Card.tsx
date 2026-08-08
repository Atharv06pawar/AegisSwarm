import * as React from "react";
import { cn } from "@/lib/utils";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: boolean;
}

export function Card({ className, glow = false, ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border border-slate-800 bg-slate-900/80 p-5 text-slate-100 shadow-lg backdrop-blur-sm transition-all duration-200 hover:border-slate-700",
        glow && "border-indigo-500/30 shadow-indigo-500/10 hover:shadow-indigo-500/20",
        className
      )}
      {...props}
    />
  );
}
