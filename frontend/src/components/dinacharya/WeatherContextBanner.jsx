import { useState } from "react";

function degToCompass(deg) {
  if (deg == null) return "";
  const dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"];
  return dirs[Math.round(deg / 22.5) % 16];
}

function uvColor(uv) {
  if (uv <= 2) return "text-green-600";
  if (uv <= 5) return "text-yellow-600";
  if (uv <= 7) return "text-orange-500";
  return "text-red-600";
}

function ChevronIcon({ expanded }) {
  return (
    <svg
      className={`h-4 w-4 text-text-faint transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
    </svg>
  );
}

function RefreshIcon({ spinning }) {
  if (spinning) {
    return (
      <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    );
  }
  return (
    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182" />
    </svg>
  );
}

function WeatherDetail({ icon, value, unit, color = "" }) {
  if (value == null) return null;
  return (
    <span className={`text-xs text-text-muted ${color}`}>
      {icon} {value}
      {unit && <span className="text-text-faint">{unit}</span>}
    </span>
  );
}

export function WeatherContextBanner({ weather, refreshing, onRefresh }) {
  const [expanded, setExpanded] = useState(false);

  if (!weather) return null;

  const {
    location_name, temp_c, condition, feels_like,
    humidity, wind_speed, wind_direction, wind_gusts,
    pressure, cloud_cover, precipitation, uv_index,
    visibility, dew_point,
  } = weather;

  const handleToggle = (e) => {
    if (e.target.closest("button")) return;
    setExpanded((prev) => !prev);
  };

  const handleRefresh = (e) => {
    e.stopPropagation();
    onRefresh?.();
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={handleToggle}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); handleToggle(e); } }}
      className={`group rounded-2xl border bg-surface px-5 py-4 transition-all duration-200 cursor-pointer outline-none ${
        expanded
          ? "border-brand-200 shadow-card"
          : "border-line shadow-soft hover:shadow-card hover:border-brand-100"
      }`}
    >
      {/* Header row: always visible */}
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand transition-colors duration-200 group-hover:bg-brand-100">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z" />
            </svg>
          </div>
          <div className="min-w-0">
            {location_name && <p className="text-sm font-semibold text-text truncate">{location_name}</p>}
            <div className="flex items-center gap-x-2 flex-wrap">
              {temp_c != null && <span className="text-sm font-medium text-text">{temp_c}°C</span>}
              {condition && <span className="text-sm text-text-muted capitalize">{condition}</span>}
              {feels_like != null && (
                <span className="text-xs text-text-muted hidden sm:inline">Feels like {feels_like}°C</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
          {onRefresh && (
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-brand-50 hover:text-brand disabled:opacity-50"
              title="Refresh weather"
            >
              <RefreshIcon spinning={refreshing} />
            </button>
          )}
          <button
            onClick={() => setExpanded((prev) => !prev)}
            className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-brand-50 hover:text-brand"
            title={expanded ? "Show less" : "Show details"}
          >
            <ChevronIcon expanded={expanded} />
          </button>
        </div>
      </div>

      {/* Detail section: animated expand/collapse */}
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          expanded ? "max-h-48 opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className="mt-3 pt-3 border-t border-line-light">
          {feels_like != null && (
            <p className="text-xs text-text-muted mb-2">Feels like {feels_like}°C</p>
          )}
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5">
            <WeatherDetail icon="💧" value={humidity} unit="%" />
            <WeatherDetail icon="💨" value={wind_speed} unit={`km/h${wind_direction != null ? ` ${degToCompass(wind_direction)}` : ""}`} />
            {wind_gusts != null && <WeatherDetail icon="🌬" value={wind_gusts} unit="km/h gusts" />}
            <WeatherDetail icon="🌡" value={pressure} unit="hPa" />
            {cloud_cover != null && <span className="text-xs text-text-muted">☁ {cloud_cover}%</span>}
            {uv_index != null && <span className={`text-xs font-medium ${uvColor(uv_index)}`}>☀ UV {uv_index}</span>}
            <WeatherDetail icon="🌧" value={precipitation} unit="mm" />
            {visibility != null && (
              <span className="text-xs text-text-muted">👁 {(visibility / 1000).toFixed(0)} km</span>
            )}
            <WeatherDetail icon="💚" value={dew_point} unit="°C" />
          </div>
        </div>
      </div>
    </div>
  );
}
