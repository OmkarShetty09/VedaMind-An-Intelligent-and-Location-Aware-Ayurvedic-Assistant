import { DoshaQuiz } from "../components/dosha/DoshaQuiz.jsx";
import { DoshaResultChart } from "../components/dosha/DoshaResultChart.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";
import { useState } from "react";

export function DoshaAssessmentPage() {
  const [result, setResult] = useState(null);
  const { consentAccepted, acceptConsent } = useAuthContext();

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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-text">Dosha Assessment</h1>
        <p className="mt-1 text-sm text-text-muted">
          A short, self-reported snapshot. This is educational, not diagnostic.
        </p>
      </div>
      {result ? <DoshaResultChart result={result} /> : <DoshaQuiz onResult={setResult} />}
    </div>
  );
}
