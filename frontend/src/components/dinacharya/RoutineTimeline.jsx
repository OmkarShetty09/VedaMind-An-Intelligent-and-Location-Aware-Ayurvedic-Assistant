import { RitucharyaSeasonBadge } from "./RitucharyaSeasonBadge.jsx";

/** "06:15:00" -> "06:15" */
function hhmm(t) {
  return typeof t === "string" ? t.slice(0, 5) : "";
}

function timeWindow(act) {
  const start = hhmm(act.start);
  const end = hhmm(act.end);
  if (start && end) return `${start} – ${end}`;
  return start || "—";
}

function citationLabel(c) {
  if (typeof c === "string") return c;
  return [c.source, c.ref].filter(Boolean).join(", ");
}

/** dosha: the engine's personalization ({dominant, secondary}) when the user has taken the assessment. */
export function RoutineTimeline({ activities, seasonInfo, dosha }) {
  const doshaLabel = dosha ? [dosha.dominant, dosha.secondary].filter(Boolean).join("-") : "";
  return (
    <div className="space-y-4">
      <RitucharyaSeasonBadge info={seasonInfo} />
      <div className="relative space-y-0">
        {activities.map((act, i) => {
          const isLast = i === activities.length - 1;
          return (
            <div key={i} className="relative flex gap-4">
              <div className="flex flex-col items-center">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-50 text-xs font-semibold text-brand">
                  {i + 1}
                </div>
                {!isLast && <div className="w-px flex-1 bg-line" />}
              </div>
              <div className={`flex-1 ${isLast ? "" : "pb-4"}`}>
                <div className="rounded-xl border border-line bg-surface p-4 shadow-soft transition-all duration-150 hover:shadow-card">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-sm font-semibold text-text">{act.title}</p>
                        {act.personalized && doshaLabel && (
                          <span className="rounded-full bg-brand/10 px-2 py-0.5 text-[10px] font-medium capitalize text-brand">
                            For your {doshaLabel}
                          </span>
                        )}
                      </div>
                      {act.description && (
                        <p className="mt-1 text-sm leading-relaxed text-text-muted">{act.description}</p>
                      )}
                      {act.reasons?.length > 0 && (
                        <ul className="mt-1.5 space-y-0.5 text-xs italic text-text-faint">
                          {act.reasons.map((r, j) => (
                            <li key={j}>{r}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                    <span className="shrink-0 rounded-lg bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand">
                      {timeWindow(act)}
                    </span>
                  </div>
                  {act.citations?.length > 0 && (
                    <div className="mt-2.5 flex flex-wrap gap-2">
                      {act.citations.map((c, j) => (
                        <span key={j} className="rounded bg-brand-50/60 px-1.5 py-0.5 text-[10px] text-text-faint">
                          {citationLabel(c)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
