export function WeatherContextBanner({ weather, refreshing, onRefresh }) {
  if (!weather) return null;
  return (
    <div className="card flex items-center gap-3 px-5 py-3">
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand">
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z" />
        </svg>
      </div>
      <div className="flex-1">
        <span className="text-sm font-medium text-text">Weather</span>
        <span className="ml-2 text-sm text-text-muted">
          {weather.temp_c != null && `${weather.temp_c}°C`}
          {weather.condition && ` · ${weather.condition}`}
          {weather.humidity != null && ` · ${weather.humidity}% humidity`}
        </span>
      </div>
      {onRefresh && (
        <button
          onClick={onRefresh}
          disabled={refreshing}
          className="shrink-0 rounded-lg p-1.5 text-text-muted transition-colors hover:bg-brand-50 hover:text-brand disabled:opacity-50"
          title="Refresh weather"
        >
          {refreshing ? (
            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
            </svg>
          )}
        </button>
      )}
    </div>
  );
}
