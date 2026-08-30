import React, { useEffect, useState } from "react";
import { recommendationService } from "../services/resources";
import { getErrorMessage } from "../services/api";
import { LoadingState, ErrorState, EmptyState, useToast } from "../components/UiState";
import { RecommendationCard } from "../components/RecommendationCard";

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [generating, setGenerating] = useState(false);
  const { showToast } = useToast();

  function load() {
    setLoading(true);
    setError("");
    recommendationService
      .list()
      .then((res) => setRecommendations(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleGenerate() {
    setGenerating(true);
    try {
      const res = await recommendationService.generate();
      setRecommendations(res.data);
      showToast("Fresh recommendations generated!", "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setGenerating(false);
    }
  }

  async function handleFeedback(id, feedback) {
    try {
      await recommendationService.feedback(id, feedback);
      showToast("Thanks for the feedback - future recommendations will adapt.", "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    }
  }

  if (loading) return <LoadingState label="Loading recommendations..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-semibold">Recommendations</h1>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="text-sm px-4 py-2 rounded-lg bg-brand-600 text-white font-medium hover:bg-brand-700 disabled:opacity-50"
        >
          {generating ? "Generating..." : "Generate new recommendations"}
        </button>
      </div>
      <p className="text-slate-500 text-sm mb-6">
        Ranked using your goal, skill gaps, prerequisites, difficulty, and preferences.
      </p>

      {recommendations.length === 0 ? (
        <EmptyState
          icon="✨"
          title="No recommendations yet"
          description="Generate recommendations based on your current goal and skills."
        />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {recommendations.map((rec) => (
            <RecommendationCard key={rec.id} recommendation={rec} onFeedback={handleFeedback} />
          ))}
        </div>
      )}
    </div>
  );
}
