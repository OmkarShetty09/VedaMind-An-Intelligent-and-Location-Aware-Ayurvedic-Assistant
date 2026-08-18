import { DoshaScaleBar } from "./DoshaScaleBar.jsx";

export function DoshaResultChart({ result }) {
  if (!result?.scores) return null;
  return (
    <div className="rounded-2xl border border-line bg-surface p-6">
      <h3 className="font-semibold text-text">Your dosha profile</h3>
      <p className="mt-1 text-sm text-text-muted">
        Primary: <strong className="text-brand">{result.primary}</strong>
        {result.secondary ? `, secondary: ${result.secondary}` : ""}
      </p>
      <div className="mt-4 space-y-3">
        {Object.entries(result.scores).map(([dosha, score]) => (
          <DoshaScaleBar key={dosha} dosha={dosha} score={score} />
        ))}
      </div>
    </div>
  );
}
