import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  profileService,
  skillsService,
  learningPathService,
  progressService,
} from "../services/resources";
import { LoadingState, EmptyState } from "../components/UiState";
import ProgressBar from "../components/ProgressBar";
import SkillChart from "../components/SkillChart";

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [gap, setGap] = useState(null);
  const [path, setPath] = useState(null);
  const [pathMissing, setPathMissing] = useState(false);
  const [recentProgress, setRecentProgress] = useState([]);

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([
      profileService.get(),
      skillsService.myGaps(),
      learningPathService.get(),
      progressService.list(),
    ]).then(([profileRes, gapRes, pathRes, progressRes]) => {
      if (profileRes.status === "fulfilled") setProfile(profileRes.value.data);
      if (gapRes.status === "fulfilled") setGap(gapRes.value.data);
      if (pathRes.status === "fulfilled") setPath(pathRes.value.data);
      else setPathMissing(true);
      if (progressRes.status === "fulfilled") setRecentProgress(progressRes.value.data.slice(0, 5));
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingState label="Loading your dashboard..." />;

  if (!profile?.career_goal) {
    return (
      <EmptyState
        icon="🎯"
        title="Let's set your career goal first"
        description="Tell us what you want to become, and we'll build a personalized roadmap for you."
        action={
          <Link
            to="/goal"
            className="mt-2 text-sm px-4 py-2 rounded-lg bg-brand-600 text-white font-medium hover:bg-brand-700"
          >
            Set my goal
          </Link>
        }
      />
    );
  }

  const total = path?.items?.length || 0;
  const completed = path?.items?.filter((i) => i.status === "completed").length || 0;
  const overallPct = total ? Math.round((completed / total) * 100) : 0;

  const currentItem = path?.items?.find((i) => i.status !== "completed");
  const nextAction = currentItem;

  const skillChartData = (gap?.required_skills || []).map((s) => ({
    skill: s.skill_name,
    proficiency: s.proficiency,
    target: 100,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Welcome back{profile ? "" : ""} 👋</h1>
        <p className="text-slate-500 text-sm">Here's where you stand on your {profile.career_goal} journey.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2 bg-white border border-slate-200 rounded-xl p-5">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold text-slate-900">{profile.career_goal} Roadmap</h2>
            <span className="text-sm font-bold text-brand-700">{overallPct}%</span>
          </div>
          <ProgressBar value={overallPct} showLabel={false} />
          <p className="text-xs text-slate-500 mt-2">
            {pathMissing
              ? "No learning path generated yet."
              : `${completed} of ${total} milestones complete`}
          </p>
          {pathMissing && (
            <Link to="/learning-path" className="text-sm text-brand-600 font-medium hover:underline mt-2 inline-block">
              Generate your roadmap →
            </Link>
          )}
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h2 className="font-semibold text-slate-900 mb-2 text-sm">Profile</h2>
          <dl className="text-sm space-y-1.5">
            <div className="flex justify-between">
              <dt className="text-slate-500">Level</dt>
              <dd className="font-medium">{profile.experience_level}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Weekly hours</dt>
              <dd className="font-medium">{profile.weekly_hours}h</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Style</dt>
              <dd className="font-medium">{profile.preferred_learning_style || "Not set"}</dd>
            </div>
          </dl>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h2 className="font-semibold text-slate-900 mb-2">Skill overview</h2>
          <SkillChart data={skillChartData} />
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5">
          <h2 className="font-semibold text-slate-900 mb-3">Next action</h2>
          {nextAction ? (
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">
                Phase {nextAction.phase_order}
              </p>
              <p className="font-semibold text-slate-900">{nextAction.resource.title}</p>
              <p className="text-sm text-slate-500 mt-1">
                Estimated time: {nextAction.resource.estimated_hours}h
              </p>
              {nextAction.reasons?.[0] && (
                <p className="text-sm text-slate-600 mt-2 bg-slate-50 rounded-lg p-2.5">
                  Why: {nextAction.reasons[0]}
                </p>
              )}
              <Link
                to="/learning-path"
                className="text-sm text-brand-600 font-medium hover:underline mt-3 inline-block"
              >
                View full roadmap →
              </Link>
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              {pathMissing ? "Generate a learning path to see your next action." : "You've completed everything on your current path! 🎉"}
            </p>
          )}
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-5">
        <h2 className="font-semibold text-slate-900 mb-3">Recent activity</h2>
        {recentProgress.length === 0 ? (
          <p className="text-sm text-slate-500">No activity logged yet.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {recentProgress.map((p) => (
              <li key={p.id} className="py-2.5 flex items-center justify-between text-sm">
                <span className="text-slate-700">{p.notes || "Study session"}</span>
                <span className="text-slate-400">{p.hours_logged}h · {new Date(p.created_at).toLocaleDateString()}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
