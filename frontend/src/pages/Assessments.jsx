import React, { useEffect, useState } from "react";
import { assessmentService } from "../services/resources";
import { getErrorMessage } from "../services/api";
import { LoadingState, ErrorState, EmptyState, useToast } from "../components/UiState";
import AssessmentCard from "../components/AssessmentCard";

export default function Assessments() {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [results, setResults] = useState({});
  const [submittingId, setSubmittingId] = useState(null);
  const { showToast } = useToast();

  function load() {
    setLoading(true);
    setError("");
    assessmentService
      .list()
      .then((res) => setAssessments(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleSubmit(assessmentId, answers) {
    setSubmittingId(assessmentId);
    try {
      const res = await assessmentService.submit(assessmentId, answers);
      setResults((r) => ({ ...r, [assessmentId]: res.data }));
      showToast(`Scored ${res.data.score}% - your skill proficiency has been updated`, "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setSubmittingId(null);
    }
  }

  if (loading) return <LoadingState label="Loading assessments..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Assessments</h1>
      <p className="text-slate-500 text-sm mb-6">
        Quick skill checks - your results adapt future recommendations automatically.
      </p>

      {assessments.length === 0 ? (
        <EmptyState icon="📝" title="No assessments available" />
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          {assessments.map((a) =>
            results[a.id] ? (
              <div key={a.id} className="bg-white border border-slate-200 rounded-xl p-5">
                <h3 className="font-semibold text-slate-900 mb-2">{a.title}</h3>
                <p className="text-3xl font-bold text-brand-700">{results[a.id].score}%</p>
                <p className="text-sm text-slate-500 mt-1">
                  {results[a.id].score >= 75
                    ? "Great work! This skill is marked as strong."
                    : results[a.id].score >= 50
                    ? "Decent grasp - we'll recommend some reinforcement material."
                    : "This skill has been flagged as a gap - easier resources will be recommended."}
                </p>
              </div>
            ) : (
              <AssessmentCard
                key={a.id}
                assessment={a}
                onSubmit={(answers) => handleSubmit(a.id, answers)}
                submitting={submittingId === a.id}
              />
            )
          )}
        </div>
      )}
    </div>
  );
}
