import { RoutineEmptyState } from "./RoutineEmptyState.jsx";
import { RoutineTimeline } from "./RoutineTimeline.jsx";
import { WeatherContextBanner } from "./WeatherContextBanner.jsx";

export function DinacharyaCard({ routine, weather, weatherLoading, onRefreshWeather, loading, onRegenerate }) {
  if (loading) {
    return (
      <div className="card flex items-center justify-center p-10">
        <div className="flex items-center gap-3 text-sm text-text-muted">
          <span className="h-2 w-2 animate-pulse rounded-full bg-brand" />
          Generating your routine...
        </div>
      </div>
    );
  }
  return (
    <div className="space-y-4">
      {weather && <WeatherContextBanner weather={weather} refreshing={weatherLoading} onRefresh={onRefreshWeather} />}
      {!routine ? (
        <RoutineEmptyState onRegenerate={onRegenerate} />
      ) : (
        <RoutineTimeline activities={routine.activities || []} />
      )}
    </div>
  );
}
