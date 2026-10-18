import { Link } from "react-router-dom";

const CLASSIFICATION_LABELS = {
  single: "Single dosha",
  dual: "Dual dosha",
  tridoshic: "Tridoshic",
};

/** personalization: {assessed, dominant, secondary, classification, percentages, focus, secondary_focus} from the engine. */
export function DoshaPersonalizationBanner({ personalization }) {
  if (!personalization?.assessed) {
    return (
      <div className="card flex flex-col gap-3 border-amber-200 bg-amber-50/70 px-5 py-4 sm:flex-row sm:items-center">
        <div className="flex-1">
          <p className="text-sm font-medium text-text">This is a general routine, not yet built for you</p>
          <p className="text-xs text-text-muted">
            Take the dosha assessment and your Dinacharya will be rebuilt around your own constitution: wake time,
            massage oil, exercise, meals, breathing practice and bedtime.
          </p>
        </div>
        <Link
          to="/dosha"
          className="shrink-0 rounded-lg bg-brand px-3 py-1.5 text-center text-xs font-medium text-white transition-colors hover:bg-brand-dark"
        >
          Take the assessment
        </Link>
      </div>
    );
  }

  const { dominant, secondary, classification, percentages = {}, focus, secondary_focus: secondaryFocus } = personalization;
  return (
    <div className="card space-y-2 px-5 py-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="text-sm font-semibold text-text">
          Built for your{" "}
          <span className="capitalize">
            {dominant}
            {secondary ? `-${secondary}` : ""}
          </span>{" "}
          constitution
          {classification && (
            <span className="ml-2 text-xs font-normal text-text-faint">
              {CLASSIFICATION_LABELS[classification] || classification}
            </span>
          )}
        </p>
        {Object.keys(percentages).length > 0 && (
          <div className="flex gap-2 text-[11px] text-text-muted">
            {Object.entries(percentages).map(([d, pct]) => (
              <span key={d} className={`capitalize ${d === dominant ? "font-semibold text-brand" : ""}`}>
                {d} {pct}%
              </span>
            ))}
          </div>
        )}
      </div>
      {focus && <p className="text-xs leading-relaxed text-text-muted">{focus}</p>}
      {secondaryFocus && (
        <p className="text-xs leading-relaxed text-text-muted">
          <span className="font-medium capitalize text-text">Secondary {secondary}: </span>
          {secondaryFocus}
        </p>
      )}
      <p className="text-[11px] text-text-faint">
        Activities marked with your dosha were changed or added because of your assessment.{" "}
        <Link to="/dosha" className="underline-offset-2 hover:text-brand hover:underline">
          Retake the assessment
        </Link>
      </p>
    </div>
  );
}
