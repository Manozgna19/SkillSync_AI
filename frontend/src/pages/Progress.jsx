import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { progressService } from "../services/resources";
import { getErrorMessage } from "../services/api";
import { LoadingState, ErrorState, EmptyState, useToast } from "../components/UiState";

export default function Progress() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hours, setHours] = useState("");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const { showToast } = useToast();

  function load() {
    setLoading(true);
    setError("");
    progressService
      .list()
      .then((res) => setEntries(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleLogHours(e) {
    e.preventDefault();
    if (!hours) return;
    setSaving(true);
    try {
      await progressService.create({ hours_logged: Number(hours), notes, status: "in_progress" });
      setHours("");
      setNotes("");
      showToast("Hours logged!", "success");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <LoadingState label="Loading progress..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  const totalHours = entries.reduce((sum, e) => sum + Number(e.hours_logged || 0), 0);

  const chartData = entries
    .slice()
    .reverse()
    .slice(-10)
    .map((e) => ({
      date: new Date(e.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      hours: Number(e.hours_logged || 0),
    }));

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-1">Progress</h1>
      <p className="text-slate-500 text-sm mb-6">Total hours logged: {totalHours.toFixed(1)}h</p>

      <form onSubmit={handleLogHours} className="bg-white border border-slate-200 rounded-xl p-5 mb-6 flex gap-3 items-end flex-wrap">
        <div>
          <label className="block text-xs font-medium text-slate-700 mb-1">Hours studied</label>
          <input
            type="number"
            min="0"
            step="0.5"
            value={hours}
            onChange={(e) => setHours(e.target.value)}
            className="w-28 border border-slate-200 rounded-lg px-3 py-2 text-sm"
            placeholder="2.5"
          />
        </div>
        <div className="flex-1 min-w-[200px]">
          <label className="block text-xs font-medium text-slate-700 mb-1">Notes (optional)</label>
          <input
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
            placeholder="What did you work on?"
          />
        </div>
        <button
          type="submit"
          disabled={saving || !hours}
          className="px-4 py-2 rounded-lg bg-brand-600 text-white font-medium text-sm hover:bg-brand-700 disabled:opacity-50"
        >
          {saving ? "Logging..." : "Log hours"}
        </button>
      </form>

      {entries.length === 0 ? (
        <EmptyState icon="📈" title="No progress logged yet" description="Log your first study session above." />
      ) : (
        <>
          <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6">
            <h3 className="font-semibold text-slate-900 mb-3 text-sm">Recent study hours</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="hours" fill="#3d66f5" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl divide-y divide-slate-100">
            {entries.map((e) => (
              <div key={e.id} className="p-4 flex items-center justify-between text-sm">
                <div>
                  <p className="font-medium text-slate-800">{e.notes || "Study session"}</p>
                  <p className="text-xs text-slate-400">{new Date(e.created_at).toLocaleString()}</p>
                </div>
                <span className="font-semibold text-brand-700">{e.hours_logged}h</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
