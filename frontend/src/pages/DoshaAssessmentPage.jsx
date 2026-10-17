import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { DoshaResultChart } from "../components/dosha/DoshaResultChart.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";
import { clearResult, loadProfile, loadQuiz, submitQuiz } from "../store/doshaSlice.js";
import { store } from "../store/index.js";


export function DoshaAssessmentPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [retake, setRetake] = useState(false);
  const { consentAccepted, acceptConsent } = useAuthContext();
  const { result, profile, error, quiz, quizError } = useSelector((s) => s.dosha);
  // Questions and dosha descriptions are managed in the admin (QuizQuestion / DoshaInfo).
  const ALL_QUESTIONS = quiz?.questions || [];

  useEffect(() => {
    store.dispatch(loadProfile());
    if (!quiz) store.dispatch(loadQuiz());
  }, [quiz]);

  useEffect(() => {
    if (result?.results) {
      store.dispatch(loadProfile());
    }
  }, [result]);

  if (!consentAccepted) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="page-title">Dosha Assessment</h1>
          <p className="page-subtitle">
            A short, self-reported snapshot. This is educational, not diagnostic.
          </p>
        </div>
        <div className="card p-6 space-y-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-lg">⚠️</div>
            <h2 className="text-lg font-semibold text-text">Please read before continuing</h2>
          </div>
          <div className="space-y-3 text-sm leading-relaxed text-text-muted">
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
            className="rounded-xl bg-brand px-5 py-2.5 text-sm font-medium text-white transition-all duration-150 hover:bg-brand-dark active:scale-[0.98]"
          >
            I understand — continue
          </button>
        </div>
      </div>
    );
  }

  if (result?.results || (profile?.dominant_dosha && !retake)) {
    const primary = result?.results?.dominant_dosha || profile?.dominant_dosha;
    const secondary = result?.results?.secondary_dosha || profile?.secondary_dosha || "";
    // A freshly computed result carries `scores`; a stored profile keeps them as `vikriti_scores`.
    const scores = result?.results?.scores || profile?.scores || profile?.vikriti_scores || {};
    const total = Object.values(scores).reduce((a, b) => a + b, 0) || 1;
    const percentages =
      result?.results?.percentages ||
      Object.fromEntries(Object.entries(scores).map(([d, c]) => [d, Math.round((c / total) * 1000) / 10]));
    const classification = result?.results?.classification || (secondary ? "dual" : "single");

    return (
      <div className="space-y-6">
        <div>
          <h1 className="page-title">Your Dosha Profile</h1>
          <p className="page-subtitle">
            A short, self-reported snapshot. This is educational, not diagnostic.
          </p>
        </div>
        <DoshaResultChart
          doshas={quiz?.doshas || []}
          result={{ primary, secondary, scores, percentages, classification }}
        />
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => {
              dispatch(clearResult());
              navigate("/chat");
            }}
            className="rounded-xl bg-brand px-5 py-2.5 text-sm font-medium text-white transition-all duration-150 hover:bg-brand-dark active:scale-[0.98]"
          >
            Start chatting
          </button>
          <button
            onClick={() => {
              dispatch(clearResult());
              setAnswers({});
              setStep(0);
              setRetake(true);
            }}
            className="rounded-xl border border-line px-5 py-2.5 text-sm font-medium text-text-muted transition-all duration-150 hover:bg-brand-50 hover:text-text"
          >
            Retake assessment
          </button>
        </div>
      </div>
    );
  }

  if (!ALL_QUESTIONS.length) {
    return (
      <div className="card p-6 text-sm text-text-muted">
        {quizError ? `Could not load the quiz: ${quizError}` : "Loading the assessment..."}
      </div>
    );
  }

  const current = ALL_QUESTIONS[Math.min(step, ALL_QUESTIONS.length - 1)];
  const progress = ((step + 1) / ALL_QUESTIONS.length) * 100;
  const answered = Object.keys(answers).length;

  const selectOption = (key, idx) => {
    setAnswers((prev) => ({ ...prev, [key]: idx }));
    if (step < ALL_QUESTIONS.length - 1) {
      setTimeout(() => setStep((s) => s + 1), 250);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    const res = await dispatch(submitQuiz(answers));
    setSubmitting(false);
    if (res.type?.endsWith("/fulfilled")) setRetake(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Dosha Assessment</h1>
        <p className="page-subtitle">
          A short, self-reported snapshot. This is educational, not diagnostic.
        </p>
      </div>

      <div className="card px-5 py-4">
        <div className="mb-3 flex items-center justify-between text-xs text-text-muted">
          <span className="font-medium">
            Question {step + 1} of {ALL_QUESTIONS.length}
          </span>
          <span>{current.section}</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-brand-100">
          <div
            className="h-full rounded-full bg-brand transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <fieldset className="card p-6">
        <legend className="text-base font-semibold text-text">{current.prompt}</legend>
        <div className="mt-5 space-y-3">
          {current.options.map((opt, idx) => (
            <button
              key={idx}
              onClick={() => selectOption(current.key, idx)}
              className={`w-full rounded-xl border px-5 py-4 text-left text-sm transition-all duration-150 ${
                answers[current.key] === idx
                  ? "border-brand bg-brand text-white shadow-sm"
                  : "border-line bg-white text-text hover:border-brand/40 hover:bg-brand-50/50"
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      </fieldset>

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <div className="flex items-center justify-between">
        <button
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={step === 0}
          className="rounded-xl border border-line px-5 py-2.5 text-sm font-medium text-text-muted transition-all duration-150 hover:bg-brand-50 hover:text-text disabled:opacity-40 disabled:hover:bg-transparent"
        >
          Back
        </button>
        {step === ALL_QUESTIONS.length - 1 ? (
          <button
            onClick={handleSubmit}
            disabled={answered < ALL_QUESTIONS.length || submitting}
            className="rounded-xl bg-brand px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-150 hover:bg-brand-dark hover:shadow-md disabled:opacity-50"
          >
            {submitting ? "Computing..." : "See my dosha"}
          </button>
        ) : (
          <button
            onClick={() => setStep((s) => Math.min(ALL_QUESTIONS.length - 1, s + 1))}
            disabled={answers[current.key] === undefined}
            className="rounded-xl bg-brand px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-150 hover:bg-brand-dark hover:shadow-md disabled:opacity-50"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
