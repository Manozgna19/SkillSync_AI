import React, { useState } from "react";

export default function AssessmentCard({ assessment, onSubmit, submitting }) {
  const [answers, setAnswers] = useState(Array(assessment.questions.length).fill(null));

  const allAnswered = answers.every((a) => a !== null);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-5">
      <h3 className="font-semibold text-slate-900">{assessment.title}</h3>
      {assessment.questions.map((q, qi) => (
        <div key={qi} className="space-y-2">
          <p className="text-sm font-medium text-slate-800">
            {qi + 1}. {q.question}
          </p>
          <div className="grid gap-2">
            {q.options.map((opt, oi) => (
              <label
                key={oi}
                className={`text-sm px-3 py-2 rounded-lg border cursor-pointer transition-colors ${
                  answers[qi] === oi
                    ? "border-brand-500 bg-brand-50 text-brand-800"
                    : "border-slate-200 hover:bg-slate-50"
                }`}
              >
                <input
                  type="radio"
                  name={`q-${qi}`}
                  className="mr-2 accent-brand-600"
                  checked={answers[qi] === oi}
                  onChange={() => {
                    const next = [...answers];
                    next[qi] = oi;
                    setAnswers(next);
                  }}
                />
                {opt}
              </label>
            ))}
          </div>
        </div>
      ))}
      <button
        disabled={!allAnswered || submitting}
        onClick={() => onSubmit(answers)}
        className="w-full py-2.5 rounded-lg bg-brand-600 text-white font-medium text-sm disabled:opacity-40"
      >
        {submitting ? "Submitting..." : "Submit answers"}
      </button>
    </div>
  );
}
