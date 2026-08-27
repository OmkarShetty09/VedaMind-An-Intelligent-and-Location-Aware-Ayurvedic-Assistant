import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { DoshaResultChart } from "../components/dosha/DoshaResultChart.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";
import { clearResult, loadProfile, submitQuiz } from "../store/doshaSlice.js";
import { store } from "../store/index.js";

const STEPS = [
  { key: "frame", q: "My body frame is...", options: ["Lean and light", "Medium and balanced", "Large and sturdy"] },
  { key: "digestion", q: "My digestion is usually...", options: ["Irregular / sensitive", "Moderate", "Slow and steady"] },
  { key: "energy", q: "My energy pattern is...", options: ["Bursts, then tired", "Steady through the day", "Slow to start, steady"] },
  { key: "sleep", q: "My sleep is...", options: ["Light / interrupted", "Moderate", "Deep and long"] },
  { key: "skin", q: "My skin tends to be...", options: ["Dry", "Sensitive / warm", "Oily / cool"] },
  { key: "appetite", q: "My appetite is...", options: ["Variable, I forget to eat", "Strong, I get irritable if hungry", "Steady, I can skip meals"] },
  { key: "temperature", q: "I prefer...", options: ["Warm environments", "Cool environments", "Neither extremes"] },
  { key: "stress", q: "Under stress I become...", options: ["Anxious and scattered", "Irritable and sharp", "Slow and withdrawn"] },
];

export function DoshaAssessmentPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const { consentAccepted, acceptConsent } = useAuthContext();
  const { result, profile, status } = useSelector((s) => s.dosha);
  const fromChat = window.location.state?.fromChat;

  useEffect(() => {
    store.dispatch(loadProfile());
  }, []);

  useEffect(() => {
    if (result?.results) {
      store.dispatch(loadProfile());
    }
  }, [result]);

  if (!consentAccepted) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-text">Dosha Assessment</h1>
          <p className="mt-1 text-sm text-text-muted">
            A short, self-reported snapshot. This is educational, not diagnostic.
          </p>
        </div>
        <div className="rounded-xl border border-line bg-surface p-6 space-y-4">
          <h2 className="text-lg font-semibold text-text">Please read before continuing</h2>
          <div className="space-y-2 text-sm leading-relaxed text-text-muted">
            <p>
              VedaMind provides educational wellness guidance based on classical Ayurvedic texts. It is <strong>not</strong>{" "}
              a medical device and does not provide diagnosis, treatment, or medical advice.
            </p>
            <p>
              Do not stop, start, or change any prescribed medication based on this app. If you are pregnant, nursing, or
              caring for a child, be especially careful: some herbs are not suitable.
            </p>
            <p>For any medical concern, please consult a qualified healthcare provider.</p>
          </div>
          <button
            onClick={() => acceptConsent()}
            className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark transition-colors"
          >
            I understand — continue
          </button>
        </div>
      </div>
    );
  }

  if (result?.results || (profile?.dominant_dosha && fromChat)) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold text-text">Your Dosha Profile</h1>
          <p className="mt-1 text-sm text-text-muted">
            Based on your answers, you are a{" "}
            <strong className="text-brand">
              {result?.results?.primary || profile?.dominant_dosha}
            </strong>
            {result?.results?.secondary ? ` with secondary ${result.results.secondary}` : ""} type.
          </p>
        </div>
        <DoshaResultChart
          result={{
            primary: result?.results?.primary || profile?.dominant_dosha,
            secondary: result?.results?.secondary,
            scores: result?.results?.scores || profile?.scores || {},
          }}
        />
        {fromChat && (
          <button
            onClick={() => {
              dispatch(clearResult());
              navigate("/chat");
            }}
            className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark transition-colors"
          >
            Start chatting
          </button>
        )}
      </div>
    );
  }

  const current = STEPS[step];
  const progress = ((step + 1) / STEPS.length) * 100;
  const answered = Object.keys(answers).length;

  const selectOption = (key, idx) => {
    setAnswers((prev) => ({ ...prev, [key]: idx }));
    if (step < STEPS.length - 1) {
      setTimeout(() => setStep((s) => s + 1), 200);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    await dispatch(submitQuiz(answers));
    setSubmitting(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text">Dosha Assessment</h1>
        <p className="mt-1 text-sm text-text-muted">
          A short, self-reported snapshot. This is educational, not diagnostic.
        </p>
      </div>

      <div className="rounded-xl border border-line bg-surface p-4">
        <div className="mb-4 flex items-center justify-between text-xs text-text-muted">
          <span>
            Question {step + 1} of {STEPS.length}
          </span>
          <span>{answered} answered</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-brand-light">
          <div
            className="h-full rounded-full bg-brand transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <fieldset className="rounded-xl border border-line bg-surface p-6">
        <legend className="text-base font-medium text-text">{current.q}</legend>
        <div className="mt-4 space-y-2">
          {current.options.map((opt, idx) => (
            <button
              key={idx}
              onClick={() => selectOption(current.key, idx)}
              className={`w-full rounded-xl border px-4 py-3 text-left text-sm transition-colors ${
                answers[current.key] === idx
                  ? "border-brand bg-brand text-white"
                  : "border-line bg-white text-text hover:border-brand"
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      </fieldset>

      <div className="flex items-center justify-between">
        <button
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={step === 0}
          className="rounded-lg border border-line px-4 py-2 text-sm text-text-muted hover:bg-surface disabled:opacity-40"
        >
          Back
        </button>
        {step === STEPS.length - 1 ? (
          <button
            onClick={handleSubmit}
            disabled={answered < STEPS.length || submitting}
            className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark transition-colors disabled:opacity-50"
          >
            {submitting ? "Computing..." : "See my dosha"}
          </button>
        ) : (
          <button
            onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))}
            disabled={!answers[current.key]}
            className="rounded-lg bg-brand px-4 py-2 text-sm font-medium text-white hover:bg-brand-dark transition-colors disabled:opacity-50"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
