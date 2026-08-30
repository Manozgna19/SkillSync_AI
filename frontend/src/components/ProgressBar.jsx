import React from "react";

export default function ProgressBar({ value, className = "", showLabel = true, color = "brand" }) {
  const pct = Math.max(0, Math.min(100, value || 0));
  const colorClasses = {
    brand: "bg-brand-600",
    accent: "bg-accent-500",
  };
  return (
    <div className={`w-full ${className}`}>
      <div className="flex items-center justify-between mb-1">
        {showLabel && <span className="text-xs font-medium text-slate-500">{pct}% complete</span>}
      </div>
      <div className="h-2.5 w-full bg-slate-200 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses[color] || colorClasses.brand} rounded-full transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
