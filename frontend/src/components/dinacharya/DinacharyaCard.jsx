import { RoutineEmptyState } from "./RoutineEmptyState.jsx";
import { RoutineTimeline } from "./RoutineTimeline.jsx";
import { WeatherContextBanner } from "./WeatherContextBanner.jsx";

export function DinacharyaCard({ routine, weather, loading, onRegenerate }) {
  if (loading) return <div className="rounded-2xl border border-line bg-surface p-6">Loading your routine...</div>;
  if (!routine) return <RoutineEmptyState onRegenerate={onRegenerate} />;
  return (
    <div className="space-y-4">
      {weather && <WeatherContextBanner weather={weather} />}
      <RoutineTimeline activities={routine.activities || []} />
    </div>
  );
}
