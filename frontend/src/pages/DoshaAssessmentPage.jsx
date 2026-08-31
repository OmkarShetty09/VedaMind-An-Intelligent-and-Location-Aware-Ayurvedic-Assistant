import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { DoshaResultChart } from "../components/dosha/DoshaResultChart.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";
import { clearResult, loadProfile, submitQuiz } from "../store/doshaSlice.js";
import { store } from "../store/index.js";

const STEPS = [
  {
    section: "Physical Characteristics",
    questions: [
      {
        key: "body_frame",
        q: "Body Frame & Build",
        options: [
          "Slender, light, thin frame; hard to gain weight.",
          "Medium, athletic build; moderate muscle tone; can gain/lose weight easily.",
          "Solid, large, broad frame; sturdy build; gains weight easily, loses it slowly.",
        ],
      },
      {
        key: "skin_type",
        q: "Skin Type",
        options: [
          "Dry, rough, thin, cool to the touch, prone to cracking.",
          "Warm, reddish, oily in the T-zone, prone to inflammation, acne, or freckles.",
          "Thick, smooth, moist, soft, cool, oily skin.",
        ],
      },
      {
        key: "hair_texture",
        q: "Hair Texture",
        options: [
          "Dry, thin, coarse, curly, or prone to split ends.",
          "Fine, straight, soft, early graying or thinning/balding.",
          "Thick, dark, wavy, lustrous, and strong.",
        ],
      },
      {
        key: "joints_mobility",
        q: "Joints & Mobility",
        options: [
          "Small joints; prominent bones; joints tend to crack or pop.",
          "Flexible, medium-sized joints; warm and comfortable.",
          "Large, sturdy, well-padded joints with high flexibility.",
        ],
      },
    ],
  },
  {
    section: "Physiology & Metabolism",
    questions: [
      {
        key: "appetite_digestion",
        q: "Appetite & Digestion",
        options: [
          "Irregular, variable appetite; prone to gas, bloating, or constipation.",
          "Strong, intense appetite; gets irritable if meals are delayed; prone to acid reflux.",
          "Steady, slow appetite; can skip meals easily without discomfort; slow digestion.",
        ],
      },
      {
        key: "climate_preference",
        q: "Weather & Climate Preference",
        options: [
          "Dislikes cold and wind; loves warm, humid climates.",
          "Dislikes heat and bright sun; prefers cool, well-ventilated places.",
          "Dislikes cold and damp/rainy weather; prefers warm, dry environments.",
        ],
      },
      {
        key: "sleep_quality",
        q: "Sleep Quality",
        options: [
          "Light sleeper, restless, easily awakened, prone to insomnia.",
          "Sound, moderate sleeper (6–8 hours); can wake up easily if needed.",
          "Deep, heavy sleeper (8+ hours); finds it hard to wake up in the morning.",
        ],
      },
      {
        key: "energy_stamina",
        q: "Energy & Stamina",
        options: [
          "Bursts of high energy followed by sudden fatigue; low endurance.",
          "High, focused energy; strong stamina; driven to accomplish goals.",
          "Steady, reliable energy; high endurance, but takes time to get started.",
        ],
      },
    ],
  },
  {
    section: "Mind, Emotions & Behavior",
    questions: [
      {
        key: "learning_memory",
        q: "Learning & Memory Style",
        options: [
          "Learns very quickly, but forgets quickly too.",
          "Medium-paced learner; distinct understanding; remembers what is useful.",
          "Learns slowly, but retains information for a long time (strong long-term memory).",
        ],
      },
      {
        key: "stress_reaction",
        q: "Reaction to Stress",
        options: [
          "Anxiety, worry, fear, overthinking, agitation.",
          "Anger, impatience, frustration, irritability, criticism.",
          "Stubbornness, withdrawal, complacency, emotional eating.",
        ],
      },
      {
        key: "spending_habits",
        q: "Spending & Money Habits",
        options: [
          "Impulsive spender; spends money quickly on short-term wants.",
          "Spends money intentionally on quality, luxury, or practical items.",
          "Saver by nature; accumulates wealth and hates spending unnecessarily.",
        ],
      },
    ],
  },
];

const ALL_QUESTIONS = STEPS.flatMap((s) => s.questions);

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

  if (result?.results || (profile?.dominant_dosha && fromChat)) {
    const primary = result?.results?.primary || profile?.dominant_dosha;
    const secondary = result?.results?.secondary_dosha || result?.results?.secondary || profile?.secondary_dosha || "";
    const scores = result?.results?.scores || profile?.scores || {};
    const percentages = result?.results?.percentages || {};
    const classification = result?.results?.classification || "single";

    return (
      <div className="space-y-6">
        <div>
          <h1 className="page-title">Your Dosha Profile</h1>
          <p className="page-subtitle">
            A short, self-reported snapshot. This is educational, not diagnostic.
          </p>
        </div>
        <DoshaResultChart
          result={{ primary, secondary, scores, percentages, classification }}
        />
        {fromChat && (
          <button
            onClick={() => {
              dispatch(clearResult());
              navigate("/chat");
            }}
            className="rounded-xl bg-brand px-5 py-2.5 text-sm font-medium text-white transition-all duration-150 hover:bg-brand-dark active:scale-[0.98]"
          >
            Start chatting
          </button>
        )}
      </div>
    );
  }

  const current = ALL_QUESTIONS[step];
  const currentSection = STEPS.find((s) => s.questions.some((q) => q.key === current.key));
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
    await dispatch(submitQuiz(answers));
    setSubmitting(false);
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
          <span>{currentSection?.section}</span>
        </div>
        <div className="h-2 overflow-hidden rounded-full bg-brand-100">
          <div
            className="h-full rounded-full bg-brand transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      <fieldset className="card p-6">
        <legend className="text-base font-semibold text-text">{current.q}</legend>
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
            disabled={!answers[current.key]}
            className="rounded-xl bg-brand px-5 py-2.5 text-sm font-medium text-white shadow-sm transition-all duration-150 hover:bg-brand-dark hover:shadow-md disabled:opacity-50"
          >
            Next
          </button>
        )}
      </div>
    </div>
  );
}
