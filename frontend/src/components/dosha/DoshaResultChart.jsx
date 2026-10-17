import { DoshaScaleBar } from "./DoshaScaleBar.jsx";

const CLASSIFICATION_LABELS = {
  single: "Single Dosha",
  dual: "Dual Dosha",
  tridoshic: "Tridoshic",
};

/** doshas: [{dosha, label, element, tagline, description}] from GET /dosha/quiz (edited in the admin). */
export function DoshaResultChart({ result, doshas = [] }) {
  if (!result?.scores) return null;

  const primary = (result.primary || result.dominant_dosha || "").toLowerCase();
  const secondary = (result.secondary || result.secondary_dosha || "").toLowerCase();
  const classification = result.classification || "single";
  const scores = result.scores;
  const percentages = result.percentages || {};
  const info = Object.fromEntries(doshas.map((d) => [d.dosha, d]));
  const primaryInfo = info[primary] || { tagline: "", description: "" };
  const totalQuestions = Object.values(scores).reduce((a, b) => a + b, 0) || 11;

  return (
    <div className="overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
      <div className="bg-gradient-to-br from-brand-50 via-surface to-brand-100/50 px-6 pt-6 pb-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-text-faint">
              {CLASSIFICATION_LABELS[classification] || "Your constitution"}
            </p>
            <h3 className="mt-1.5 text-2xl font-bold capitalize text-text">
              {primary}
              {secondary && (
                <span className="text-lg font-normal text-text-muted">-{secondary}</span>
              )}
            </h3>
            <p className="mt-1 text-sm text-text-muted">{primaryInfo.tagline}</p>
          </div>
          <div className="flex gap-1.5">
            {Object.entries(scores).map(([d, c]) => (
              <div
                key={d}
                className={`h-2 w-8 rounded-full transition-all ${
                  d === primary
                    ? "bg-brand"
                    : d === secondary
                      ? "bg-brand/40"
                      : "bg-line"
                }`}
                title={`${d}: ${c}/${totalQuestions}`}
              />
            ))}
          </div>
        </div>
        <p className="mt-4 text-sm leading-relaxed text-text-muted">
          {primaryInfo.description}
        </p>
      </div>

      <div className="space-y-2.5 px-6 pb-6 pt-3">
        {Object.entries(scores)
          .sort(([, a], [, b]) => b - a)
          .map(([dosha, count]) => (
            <DoshaScaleBar
              key={dosha}
              dosha={dosha}
              count={count}
              percentage={percentages[dosha] || 0}
              total={totalQuestions}
              isPrimary={dosha === primary}
              isSecondary={dosha === secondary}
              info={info[dosha]}
            />
          ))}
      </div>
    </div>
  );
}
