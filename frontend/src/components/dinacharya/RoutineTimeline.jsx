import { RitucharyaSeasonBadge } from "./RitucharyaSeasonBadge.jsx";

export function RoutineTimeline({ activities }) {
  return (
    <div className="relative space-y-3">
      <RitucharyaSeasonBadge />
      <div className="space-y-3">
        {activities.map((act, i) => (
          <div key={i} className="flex items-start gap-3 rounded-xl border border-line bg-surface p-4">
            <div className="w-20 shrink-0 text-sm font-medium text-brand">{act.time_window || act.time || "—"}</div>
            <div className="flex-1">
              <p className="text-sm font-medium text-text">{act.activity}</p>
              {act.description && <p className="mt-1 text-sm text-text-muted">{act.description}</p>}
              {act.sources?.length > 0 && (
                <p className="mt-1 text-xs text-text-muted">Source: {act.sources.join(", ")}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
