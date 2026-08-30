import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { goalService, learningPathService } from "../services/resources";
import { getErrorMessage } from "../services/api";
import { useToast } from "../components/UiState";

const EXAMPLES = [
  "I want to become a Machine Learning Engineer. I know Python and basic statistics, and I have about 10 hours a week.",
  "I want to become a backend developer. I know Python and SQL but I don't know APIs.",
  "I'm a complete beginner interested in frontend development and design.",
];

export default function Goal() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { showToast } = useToast();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await goalService.create(text);
      setResult(res.data);
      showToast("Goal understood! Generating your learning path...", "success");
      await learningPathService.generate();
      setTimeout(() => navigate("/learning-path"), 800);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-semibold mb-1">What's your career goal?</h1>
      <p className="text-slate-500 mb-6 text-sm">
        Describe your goal in your own words. Our AI assistant will understand it and build you a personalized roadmap.
      </p>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-6 space-y-4">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={5}
          placeholder="e.g. I want to become a Machine Learning Engineer. I know Python and basic statistics..."
          className="w-full border border-slate-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-200 resize-none"
        />
        <div className="flex flex-wrap gap-2">
          {EXAMPLES.map((ex) => (
            <button
              type="button"
              key={ex}
              onClick={() => setText(ex)}
              className="text-xs px-3 py-1.5 rounded-full border border-slate-200 hover:bg-slate-50 text-left"
            >
              {ex.slice(0, 40)}…
            </button>
          ))}
        </div>
        {error && <p className="text-sm text-rose-600">{error}</p>}
        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="px-5 py-2.5 rounded-lg bg-brand-600 text-white font-medium text-sm hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Understanding your goal..." : "Generate my learning path"}
        </button>
      </form>

      {result && (
        <div className="mt-6 bg-white border border-slate-200 rounded-xl p-6">
          <h2 className="font-semibold text-slate-900 mb-3">Here's what we understood:</h2>
          <dl className="text-sm space-y-2">
            <div className="flex gap-2">
              <dt className="font-medium text-slate-500 w-40">Goal</dt>
              <dd>{result.normalized_goal}</dd>
            </div>
            <div className="flex gap-2">
              <dt className="font-medium text-slate-500 w-40">Experience level</dt>
              <dd>{result.experience_level}</dd>
            </div>
            <div className="flex gap-2">
              <dt className="font-medium text-slate-500 w-40">Skills you mentioned</dt>
              <dd>{result.extracted_current_skills?.join(", ") || "None detected"}</dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}
