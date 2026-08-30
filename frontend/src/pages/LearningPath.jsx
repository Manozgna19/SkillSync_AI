import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { learningPathService } from "../services/resources";
import { getErrorMessage } from "../services/api";
import { LoadingState, ErrorState, EmptyState, useToast } from "../components/UiState";
import { Roadmap } from "../components/Roadmap";
import ProgressBar from "../components/ProgressBar";

export default function LearningPath() {
  const [path, setPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [generating, setGenerating] = useState(false);
  const { showToast } = useToast();

  function load() {
    setLoading(true);
    setError("");
    setNotFound(false);
    learningPathService
      .get()
      .then((res) => setPath(res.data))
      .catch((err) => {
        if (err.response?.status === 404) setNotFound(true);
        else setError(getErrorMessage(err));
      })
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleGenerate() {
    setGenerating(true);
    try {
      const res = await learningPathService.generate();
      setPath(res.data);
      setNotFound(false);
      showToast("Learning path generated!", "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setGenerating(false);
    }
  }

  async function handleStatusChange(itemId, status) {
    try {
      await learningPathService.updateItem(itemId, { status });
      load();
      showToast(status === "completed" ? "Marked as complete 🎉" : "Started!", "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  }

  if (loading) return <LoadingState label="Loading your learning path..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  if (notFound) {
    return (
      <EmptyState
        icon="🗺️"
        title="No learning path yet"
        description="Set your career goal first, then generate a personalized roadmap."
        action={
          <div className="flex gap-2 mt-2">
            <Link
              to="/goal"
              className="text-sm px-4 py-2 rounded-lg bg-brand-600 text-white font-medium hover:bg-brand-700"
            >
              Set my goal
            </Link>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="text-sm px-4 py-2 rounded-lg border border-slate-200 font-medium hover:bg-slate-50 disabled:opacity-50"
            >
              {generating ? "Generating..." : "Generate from existing profile"}
            </button>
          </div>
        }
      />
    );
  }

  const total = path.items.length;
  const completed = path.items.filter((i) => i.status === "completed").length;
  const overallPct = total ? Math.round((completed / total) * 100) : 0;

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-semibold">{path.title}</h1>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="text-sm px-4 py-2 rounded-lg border border-slate-200 font-medium hover:bg-slate-50 disabled:opacity-50"
        >
          {generating ? "Regenerating..." : "Regenerate path"}
        </button>
      </div>
      <p className="text-slate-500 text-sm mb-4">
        {completed} of {total} milestones complete
      </p>
      <div className="mb-8 max-w-md">
        <ProgressBar value={overallPct} />
      </div>

      <Roadmap items={path.items} onStatusChange={handleStatusChange} />
    </div>
  );
}
