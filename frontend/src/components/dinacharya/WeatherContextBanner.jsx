export function WeatherContextBanner({ weather }) {
  if (!weather) return null;
  return (
    <div className="card flex items-center gap-3 px-5 py-3">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand">
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z" />
        </svg>
      </div>
      <div>
        <span className="text-sm font-medium text-text">Weather</span>
        <span className="ml-2 text-sm text-text-muted">
          {weather.temp_c != null && `${weather.temp_c}°C`}
          {weather.condition && ` · ${weather.condition}`}
          {weather.humidity != null && ` · ${weather.humidity}% humidity`}
        </span>
      </div>
    </div>
  );
}
