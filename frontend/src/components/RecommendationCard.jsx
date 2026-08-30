import React from "react";

const typeColors = {
  Course: "bg-blue-50 text-blue-700",
  Video: "bg-purple-50 text-purple-700",
  Article: "bg-amber-50 text-amber-700",
  Documentation: "bg-slate-100 text-slate-700",
  Project: "bg-emerald-50 text-emerald-700",
  Assessment: "bg-rose-50 text-rose-700",
};

const difficultyColors = {
  Beginner: "text-emerald-600",
  Intermediate: "text-amber-600",
  Advanced: "text-rose-600",
};

export function CourseCard({ resource, footer }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 hover:shadow-md transition-shadow flex flex-col gap-2">
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-slate-900 leading-snug">{resource.title}</h3>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full whitespace-nowrap ${typeColors[resource.resource_type] || "bg-slate-100 text-slate-700"}`}>
          {resource.resource_type}
        </span>
      </div>
      <p className="text-sm text-slate-600 line-clamp-2">{resource.description}</p>
      <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
        <span>{resource.provider}</span>
        <span>&middot;</span>
        <span className={difficultyColors[resource.difficulty] || ""}>{resource.difficulty}</span>
        <span>&middot;</span>
        <span>{resource.estimated_hours}h</span>
      </div>
      {resource.url && (
        <a
          href={resource.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-brand-600 font-medium hover:underline w-fit"
        >
          Open resource →
        </a>
      )}
      {footer}
    </div>
  );
}

export function RecommendationCard({ recommendation, onFeedback }) {
  const [showReasons, setShowReasons] = React.useState(false);
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className="font-semibold text-slate-900">{recommendation.resource.title}</h3>
          <p className="text-xs text-slate-500 mt-0.5">
            {recommendation.resource.provider} &middot; {recommendation.resource.difficulty} &middot;{" "}
            {recommendation.resource.estimated_hours}h
          </p>
        </div>
        <span className="text-sm font-bold text-brand-700 bg-brand-50 rounded-full px-2.5 py-1 whitespace-nowrap">
          {Math.round(recommendation.score)}% match
        </span>
      </div>

      <p className="text-sm text-slate-700">{recommendation.explanation}</p>

      <button
        onClick={() => setShowReasons((s) => !s)}
        className="text-xs font-medium text-slate-500 hover:text-slate-800 w-fit"
      >
        {showReasons ? "Hide reasons" : "Why this course?"}
      </button>
      {showReasons && (
        <ul className="text-sm text-slate-600 space-y-1 bg-slate-50 rounded-lg p-3">
          {recommendation.reasons.map((r, i) => (
            <li key={i} className="flex gap-2">
              <span className="text-emerald-600">✓</span>
              {r}
            </li>
          ))}
        </ul>
      )}

      <div className="flex items-center gap-2 flex-wrap pt-1">
        {recommendation.resource.url && (
          <a
            href={recommendation.resource.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-brand-600 font-medium hover:underline mr-auto"
          >
            Open resource →
          </a>
        )}
        {onFeedback && (
          <>
            <button
              onClick={() => onFeedback(recommendation.id, "helpful")}
              className="text-xs px-2.5 py-1 rounded-full border border-slate-200 hover:bg-slate-50"
            >
              👍 Helpful
            </button>
            <button
              onClick={() => onFeedback(recommendation.id, "too_difficult")}
              className="text-xs px-2.5 py-1 rounded-full border border-slate-200 hover:bg-slate-50"
            >
              Too hard
            </button>
            <button
              onClick={() => onFeedback(recommendation.id, "too_easy")}
              className="text-xs px-2.5 py-1 rounded-full border border-slate-200 hover:bg-slate-50"
            >
              Too easy
            </button>
            <button
              onClick={() => onFeedback(recommendation.id, "not_useful")}
              className="text-xs px-2.5 py-1 rounded-full border border-slate-200 hover:bg-slate-50"
            >
              Not useful
            </button>
          </>
        )}
      </div>
    </div>
  );
}
