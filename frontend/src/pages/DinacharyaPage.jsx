import { DinacharyaCard } from "../components/dinacharya/DinacharyaCard.jsx";
import { LocationStatusPill } from "../components/location/LocationStatusPill.jsx";
import { useDinacharya } from "../hooks/useDinacharya.js";
import { useGeolocation } from "../hooks/useGeolocation.js";
import { useWeather } from "../hooks/useWeather.js";

export function DinacharyaPage() {
  const { routine, status, regenerate } = useDinacharya();
  const { permission, coords, request } = useGeolocation({ autoRequest: false });
  const { weather } = useWeather();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-text">Dinacharya</h1>
          <p className="mt-1 text-sm text-text-muted">Your daily routine, tuned to your time, season, and weather.</p>
        </div>
        <LocationStatusPill permission={permission} />
      </div>
      {!coords && permission === "unknown" && (
        <div className="rounded-xl border border-line bg-surface px-4 py-3 text-sm">
          <button className="font-medium text-brand underline" onClick={request}>
            Share your location
          </button>{" "}
          to personalize the routine.
        </div>
      )}
      <DinacharyaCard routine={routine} weather={weather} loading={status === "loading"} onRegenerate={regenerate} />
    </div>
  );
}
