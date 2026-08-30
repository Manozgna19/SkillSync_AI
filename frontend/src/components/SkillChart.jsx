import React from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

export default function SkillChart({ data }) {
  // data: [{ skill: "Python", proficiency: 80, target: 100 }, ...]
  if (!data || data.length === 0) {
    return (
      <div className="text-sm text-slate-500 flex items-center justify-center h-64">
        No skill data yet. Set your career goal to see your skill radar.
      </div>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data} outerRadius="75%">
        <PolarGrid stroke="#e2e8f0" />
        <PolarAngleAxis dataKey="skill" tick={{ fontSize: 11, fill: "#475569" }} />
        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fontSize: 10 }} />
        <Radar name="Target" dataKey="target" stroke="#94a3b8" fill="#94a3b8" fillOpacity={0.15} />
        <Radar name="Current" dataKey="proficiency" stroke="#2749ea" fill="#3d66f5" fillOpacity={0.4} />
        <Tooltip />
      </RadarChart>
    </ResponsiveContainer>
  );
}
