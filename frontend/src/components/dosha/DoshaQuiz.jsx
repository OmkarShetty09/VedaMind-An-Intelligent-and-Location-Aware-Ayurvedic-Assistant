import { useState } from "react";

import { submitQuiz } from "../../store/doshaSlice.js";
import { useDispatch } from "react-redux";
import { Button } from "../common/Button.jsx";

const QUESTIONS = [
  { key: "frame", q: "My body frame is...", options: ["Lean and light", "Medium and balanced", "Large and sturdy"] },
  { key: "digestion", q: "My digestion is usually...", options: ["Irregular / sensitive", "Moderate", "Slow and steady"] },
  { key: "energy", q: "My energy pattern is...", options: ["Bursts, then tired", "Steady through the day", "Slow to start, steady"] },
  { key: "sleep", q: "My sleep is...", options: ["Light / interrupted", "Moderate", "Deep and long"] },
  { key: "skin", q: "My skin tends to be...", options: ["Dry", "Sensitive / warm", "Oily / cool"] },
];

export function DoshaQuiz({ onResult }) {
  const dispatch = useDispatch();
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);

  const answered = Object.keys(answers).length;

  const submit = async () => {
    setLoading(true);
    const res = await dispatch(submitQuiz(answers));
    setLoading(false);
    onResult?.(res.payload);
  };

  return (
    <div className="space-y-4">
      {QUESTIONS.map((q, qi) => (
        <fieldset key={q.key} className="rounded-xl border border-line bg-surface p-4">
          <legend className="text-sm font-medium text-text">{qi + 1}. {q.q}</legend>
          <div className="mt-2 flex flex-wrap gap-2">
            {q.options.map((opt, oi) => (
              <label key={oi} className="cursor-pointer">
                <input
                  type="radio"
                  name={q.key}
                  value={oi}
                  checked={answers[q.key] === oi}
                  onChange={() => setAnswers((a) => ({ ...a, [q.key]: oi }))}
                  className="sr-only"
                />
                <span
                  className={`inline-block rounded-full border px-3 py-1.5 text-sm transition-colors ${
                    answers[q.key] === oi
                      ? "border-brand bg-brand text-white"
                      : "border-line bg-white text-text hover:border-brand"
                  }`}
                >
                  {opt}
                </span>
              </label>
            ))}
          </div>
        </fieldset>
      ))}
      <div className="flex justify-end">
        <Button loading={loading} disabled={answered < QUESTIONS.length} onClick={submit}>
          See my dosha
        </Button>
      </div>
    </div>
  );
}
