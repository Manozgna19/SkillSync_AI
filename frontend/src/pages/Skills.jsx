import React, { useEffect, useState } from "react";
import { skillsService } from "../services/resources";
import { getErrorMessage } from "../services/api";
import { LoadingState, ErrorState, useToast } from "../components/UiState";
import SkillCard from "../components/SkillCard";

export default function Skills() {
  const [skills, setSkills] = useState([]);
  const [mySkills, setMySkills] = useState({});
  const [gap, setGap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const { showToast } = useToast();

  function load() {
    setLoading(true);
    setError("");
    Promise.all([
      skillsService.list(),
      skillsService.mySkills(),
      skillsService.myGaps().catch(() => ({ data: null })),
    ])
      .then(([allSkills, mine, gapRes]) => {
        setSkills(allSkills.data);
        const map = {};
        mine.data.forEach((s) => (map[s.skill_id] = s.proficiency));
        setMySkills(map);
        setGap(gapRes.data);
      })
      .catch((err) => setError(getErrorMessage(err)))
      .finally(() => setLoading(false));
  }

  useEffect(load, []);

  function handleChange(skillId, value) {
    setMySkills((prev) => ({ ...prev, [skillId]: value }));
  }

  async function handleSave() {
    setSaving(true);
    try {
      const payload = Object.entries(mySkills).map(([skill_id, proficiency]) => ({
        skill_id,
        proficiency,
      }));
      await skillsService.updateMySkills(payload);
      showToast("Skills updated", "success");
      load();
    } catch (err) {
      showToast(getErrorMessage(err), "error");
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <LoadingState label="Loading skills..." />;
  if (error) return <ErrorState message={error} onRetry={load} />;

  const categories = [...new Set(skills.map((s) => s.category))];

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-semibold">Skills</h1>
        <button
          onClick={handleSave}
          disabled={saving}
          className="text-sm px-4 py-2 rounded-lg bg-brand-600 text-white font-medium hover:bg-brand-700 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save my skills"}
        </button>
      </div>
      <p className="text-slate-500 text-sm mb-6">
        Rate your current proficiency in each skill (0-100). This drives skill-gap analysis and recommendations.
      </p>

      {gap && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 mb-6">
          <h2 className="font-semibold text-slate-900 mb-2">Skill gap for {gap.goal}</h2>
          <div className="flex flex-wrap gap-2">
            {gap.required_skills.map((s) => (
              <span
                key={s.skill_id}
                className={`text-xs font-medium px-2.5 py-1 rounded-full ${
                  s.status === "have" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"
                }`}
              >
                {s.status === "have" ? "✓" : "✗"} {s.skill_name}
              </span>
            ))}
          </div>
        </div>
      )}

      {categories.map((category) => (
        <div key={category} className="mb-8">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-3">{category}</h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {skills
              .filter((s) => s.category === category)
              .map((skill) => (
                <SkillCard
                  key={skill.id}
                  skill={skill}
                  proficiency={mySkills[skill.id] ?? 0}
                  onChange={handleChange}
                  editable
                />
              ))}
          </div>
        </div>
      ))}
    </div>
  );
}
