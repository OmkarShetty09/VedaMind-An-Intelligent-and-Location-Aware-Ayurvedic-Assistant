export function WeatherContextBanner({ weather }) {
  if (!weather) return null;
  return (
    <div className="rounded-xl border border-line bg-surface px-4 py-3 text-sm">
      <span className="font-medium text-text">Weather context</span>
      <span className="ml-2 text-text-muted">
        {weather.temp_c != null && `${weather.temp_c}°C`}
        {weather.condition && ` · ${weather.condition}`}
        {weather.humidity != null && ` · ${weather.humidity}% humidity`}
      </span>
    </div>
  );
}
