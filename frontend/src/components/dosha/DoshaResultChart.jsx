import { DoshaScaleBar } from "./DoshaScaleBar.jsx";

const DOSHA_DESCRIPTIONS = {
  vata: {
    tagline: "Movement & creativity",
    description:
      "You are driven by air and space energy. Vata types tend to be creative, quick-thinking, and adaptable, but may experience anxiety, dry skin, or irregular digestion when imbalanced.",
  },
  pitta: {
    tagline: "Transformation & focus",
    description:
      "You are driven by fire and water energy. Pitta types tend to be ambitious, warm, and decisive, but may experience irritability, inflammation, or acid reflux when imbalanced.",
  },
  kapha: {
    tagline: "Stability & nurturing",
    description:
      "You are driven by earth and water energy. Kapha types tend to be calm, loyal, and grounded, but may experience lethargy, weight gain, or congestion when imbalanced.",
  },
};

const CLASSIFICATION_LABELS = {
  single: "Single Dosha",
  dual: "Dual Dosha",
  tridoshic: "Tridoshic",
};

export function DoshaResultChart({ result }) {
  if (!result?.scores) return null;

  const primary = (result.primary || result.dominant_dosha || "").toLowerCase();
  const secondary = (result.secondary || result.secondary_dosha || "").toLowerCase();
  const classification = result.classification || "single";
  const scores = result.scores;
  const percentages = result.percentages || {};
  const primaryInfo = DOSHA_DESCRIPTIONS[primary] || DOSHA_DESCRIPTIONS.vata;
  const totalQuestions = Object.values(scores).reduce((a, b) => a + b, 0) || 11;

  return (
    <div className="rounded-2xl border border-line bg-surface overflow-hidden">
      <div className="bg-gradient-to-br from-brand/5 via-transparent to-brand/10 px-6 pt-6 pb-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
              {CLASSIFICATION_LABELS[classification] || "Your constitution"}
            </p>
            <h3 className="mt-1 text-2xl font-bold capitalize text-text">
              {primary}
              {secondary && (
                <span className="text-lg font-normal text-text-muted">-{secondary}</span>
              )}
            </h3>
            <p className="mt-1 text-sm text-text-muted">{primaryInfo.tagline}</p>
          </div>
          <div className="flex gap-1">
            {Object.entries(scores).map(([d, c]) => (
              <div
                key={d}
                className={`h-2 w-8 rounded-full ${
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
        <p className="mt-3 text-sm leading-relaxed text-text-muted">
          {primaryInfo.description}
        </p>
      </div>

      <div className="px-6 pb-5 pt-2 space-y-2">
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
            />
          ))}
      </div>
    </div>
  );
}
