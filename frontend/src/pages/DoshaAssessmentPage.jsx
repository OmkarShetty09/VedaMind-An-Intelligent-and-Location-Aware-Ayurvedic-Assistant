import { DoshaQuiz } from "../components/dosha/DoshaQuiz.jsx";
import { DoshaResultChart } from "../components/dosha/DoshaResultChart.jsx";
import { useState } from "react";

export function DoshaAssessmentPage() {
  const [result, setResult] = useState(null);
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
