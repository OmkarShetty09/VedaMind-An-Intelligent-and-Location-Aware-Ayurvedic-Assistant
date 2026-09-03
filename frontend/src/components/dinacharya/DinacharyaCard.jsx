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
      {routine && (
        <div className="flex justify-end">
          <button
            onClick={onRegenerate}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-text-muted transition-colors hover:bg-brand-50 hover:text-brand disabled:opacity-50"
          >
            <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
            </svg>
            Regenerate
          </button>
        </div>
      )}
      {!routine ? (
        <RoutineEmptyState onRegenerate={onRegenerate} />
      ) : (
        <RoutineTimeline activities={routine.activities || []} />
      )}
    </div>
  );
}
