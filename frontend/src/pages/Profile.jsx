import React, { useEffect, useState } from "react";
import { profileService } from "../services/resources";
import { getErrorMessage } from "../services/api";
import { LoadingState, ErrorState, useToast } from "../components/UiState";

const EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"];
const LEARNING_STYLES = ["Visual", "Reading", "Hands-on", "Mixed"];

export default function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const { showToast } = useToast();

  function load() {
    setLoading(true);
    setError("");
    profileService
      .get()
      .then((res) => setProfile(res.data))
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        experience_level: profile.experience_level,
        occupation: profile.occupation,
        career_goal: profile.career_goal,
        interests: profile.interests,
        preferred_learning_style: profile.preferred_learning_style,
        weekly_hours: profile.weekly_hours ? Number(profile.weekly_hours) : undefined,
      };
      const res = await profileService.update(payload);
      setProfile(res.data);
      showToast("Profile saved", "success");
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <LoadingState label="Loading your profile..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!profile) return null;

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-semibold mb-1">Learner Profile</h1>
      <p className="text-slate-500 mb-6 text-sm">
        Tell us about yourself so we can personalize your learning path.
      </p>

      <form onSubmit={handleSave} className="bg-white border border-slate-200 rounded-xl p-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Experience level</label>
          <select
            value={profile.experience_level || "Beginner"}
            onChange={(e) => setProfile({ ...profile, experience_level: e.target.value })}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
          >
            {EXPERIENCE_LEVELS.map((lvl) => (
              <option key={lvl} value={lvl}>
                {lvl}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Current occupation / status</label>
          <input
            value={profile.occupation || ""}
            onChange={(e) => setProfile({ ...profile, occupation: e.target.value })}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
            placeholder="e.g. Computer Science student"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Career goal</label>
          <input
            value={profile.career_goal || ""}
            onChange={(e) => setProfile({ ...profile, career_goal: e.target.value })}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
            placeholder="e.g. Machine Learning Engineer"
          />
          <p className="text-xs text-slate-400 mt-1">
            Tip: use the Goal page to set this from a natural-language description instead.
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Interests (comma separated)</label>
          <input
            value={(profile.interests || []).join(", ")}
            onChange={(e) =>
              setProfile({
                ...profile,
                interests: e.target.value.split(",").map((s) => s.trim()).filter(Boolean),
              })
            }
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
            placeholder="e.g. web apps, data, robotics"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Preferred learning style</label>
          <select
            value={profile.preferred_learning_style || ""}
            onChange={(e) => setProfile({ ...profile, preferred_learning_style: e.target.value })}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Select a style</option>
            {LEARNING_STYLES.map((style) => (
              <option key={style} value={style}>
                {style}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Weekly available hours</label>
          <input
            type="number"
            min={1}
            max={80}
            value={profile.weekly_hours || 5}
            onChange={(e) => setProfile({ ...profile, weekly_hours: e.target.value })}
            className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm"
          />
        </div>

        <button
          type="submit"
          disabled={saving}
          className="px-5 py-2.5 rounded-lg bg-brand-600 text-white font-medium text-sm hover:bg-brand-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save profile"}
        </button>
      </form>
    </div>
  );
}
