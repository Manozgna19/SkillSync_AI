import React from "react";

export default function SkillCard({ skill, proficiency, onChange, editable }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h4 className="font-medium text-slate-900">{skill.name}</h4>
        <span className="text-xs text-slate-500 bg-slate-100 rounded-full px-2 py-0.5">{skill.category}</span>
      </div>
      {skill.description && <p className="text-xs text-slate-500 line-clamp-2">{skill.description}</p>}
      <div className="flex items-center gap-2 mt-1">
        <input
          type="range"
          min={0}
          max={100}
          step={5}
          value={proficiency ?? 0}
          disabled={!editable}
          onChange={(e) => onChange && onChange(skill.id, Number(e.target.value))}
          className="flex-1 accent-brand-600"
        />
        <span className="text-xs font-semibold text-slate-600 w-9 text-right">{proficiency ?? 0}%</span>
      </div>
    </div>
  );
}
