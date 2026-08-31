import { RitucharyaSeasonBadge } from "./RitucharyaSeasonBadge.jsx";

export function RoutineTimeline({ activities }) {
  return (
    <div className="space-y-4">
      <RitucharyaSeasonBadge />
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
                      <p className="text-sm font-semibold text-text">{act.activity}</p>
                      {act.description && (
                        <p className="mt-1 text-sm leading-relaxed text-text-muted">{act.description}</p>
                      )}
                    </div>
                    <span className="shrink-0 rounded-lg bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand">
                      {act.time_window || act.time || "—"}
                    </span>
                  </div>
                  {act.sources?.length > 0 && (
                    <div className="mt-2.5 flex flex-wrap gap-1">
                      {act.sources.map((s, j) => (
                        <span key={j} className="text-[10px] text-text-faint">{s}</span>
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
