import React from "react";
import ProgressBar from "./ProgressBar";

const statusStyles = {
  completed: { icon: "✓", classes: "bg-emerald-500 text-white border-emerald-500" },
  in_progress: { icon: "→", classes: "bg-brand-600 text-white border-brand-600" },
  not_started: { icon: "○", classes: "bg-white text-slate-400 border-slate-300" },
};

export function MilestoneCard({ item, onStatusChange }) {
  const style = statusStyles[item.status] || statusStyles.not_started;
  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className={`w-9 h-9 rounded-full border-2 flex items-center justify-center font-bold text-sm ${style.classes}`}>
          {style.icon}
        </div>
        <div className="w-0.5 flex-1 bg-slate-200 my-1" />
      </div>
      <div className="bg-white border border-slate-200 rounded-xl p-4 flex-1 mb-4">
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Phase {item.phase_order}</p>
            <h3 className="font-semibold text-slate-900">{item.resource.title}</h3>
          </div>
          {item.recommendation_score != null && (
            <span className="text-xs font-semibold text-brand-700 bg-brand-50 rounded-full px-2 py-0.5 whitespace-nowrap">
              {Math.round(item.recommendation_score)}% match
            </span>
          )}
        </div>
        <p className="text-sm text-slate-600 mt-1 line-clamp-2">{item.resource.description}</p>
        <div className="flex items-center gap-3 text-xs text-slate-500 mt-2">
          <span>{item.resource.provider}</span>
          <span>&middot;</span>
          <span>{item.resource.difficulty}</span>
          <span>&middot;</span>
          <span>{item.resource.estimated_hours}h</span>
        </div>

        <div className="mt-3">
          <ProgressBar value={item.completion_percentage} />
        </div>

        <div className="flex items-center gap-2 mt-3 flex-wrap">
          {item.resource.url && (
            <a
              href={item.resource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-brand-600 font-medium hover:underline mr-auto"
            >
              Open resource →
            </a>
          )}
          {onStatusChange && item.status !== "completed" && (
            <button
              onClick={() => onStatusChange(item.id, "completed")}
              className="text-xs px-3 py-1.5 rounded-full bg-emerald-500 text-white font-medium hover:bg-emerald-600"
            >
              Mark complete
            </button>
          )}
          {onStatusChange && item.status === "not_started" && (
            <button
              onClick={() => onStatusChange(item.id, "in_progress")}
              className="text-xs px-3 py-1.5 rounded-full border border-slate-200 font-medium hover:bg-slate-50"
            >
              Start
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export function Roadmap({ items, onStatusChange }) {
  if (!items || items.length === 0) {
    return null;
  }
  return (
    <div>
      {items.map((item, idx) => (
        <MilestoneCard
          key={item.id}
          item={{ ...item, isLast: idx === items.length - 1 }}
          onStatusChange={onStatusChange}
        />
      ))}
    </div>
  );
}
