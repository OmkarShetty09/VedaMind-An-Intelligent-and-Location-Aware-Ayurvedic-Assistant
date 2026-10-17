import { useState } from "react";

import { DinacharyaCard } from "../components/dinacharya/DinacharyaCard.jsx";
import { CityPicker } from "../components/location/CityPicker.jsx";
import { LocationStatusPill } from "../components/location/LocationStatusPill.jsx";
import { useDinacharya } from "../hooks/useDinacharya.js";
import { useGeolocation } from "../hooks/useGeolocation.js";
import { useWeather } from "../hooks/useWeather.js";

export function DinacharyaPage() {
  const { routine, status, error, regenerate } = useDinacharya();
  const { permission, coords, request } = useGeolocation({ autoRequest: false });
  const { weather, status: weatherStatus, refetchWeather } = useWeather();
  const [changingCity, setChangingCity] = useState(false);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="page-title">Dinacharya</h1>
          <p className="page-subtitle">Your daily routine, tuned to your time, season, and weather.</p>
        </div>
        <LocationStatusPill permission={!coords && weather ? "manual" : permission} />
      </div>
      {/* The browser blocked/can't do geolocation and no location is saved yet: let the user type a city. */}
      {!coords && !weather && (permission === "denied" || permission === "unsupported") && (
        <div className="card space-y-3 px-5 py-4">
          <div className="flex items-start gap-3">
            <div className="flex-1">
              <p className="text-sm font-medium text-text">Location is blocked in this browser</p>
              <p className="text-xs text-text-muted">
                Pick your city instead, so sunrise, sunset and weather are right. (Or allow location in the browser&apos;s
                site settings and press Retry.)
              </p>
            </div>
            <button
              onClick={request}
              className="shrink-0 rounded-lg border border-line px-3 py-1.5 text-xs font-medium text-text-muted transition-colors hover:bg-brand-50"
            >
              Retry
            </button>
          </div>
          <CityPicker onSaved={regenerate} />
        </div>
      )}
      {(coords || weather) && (
        <div className="flex justify-end">
          <button
            onClick={() => setChangingCity((v) => !v)}
            className="text-xs font-medium text-text-muted underline-offset-2 hover:text-brand hover:underline"
          >
            {changingCity ? "Cancel" : "Change city"}
          </button>
        </div>
      )}
      {changingCity && (
        <div className="card px-5 py-4">
          <CityPicker
            onSaved={() => {
              setChangingCity(false);
              regenerate();
            }}
          />
        </div>
      )}
      {!coords && !weather && permission === "unknown" && (
        <div className="card flex items-center gap-3 px-5 py-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand">
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-text">Enable location for a personalized routine</p>
            <p className="text-xs text-text-muted">Uses your local time, sunrise/sunset, and season.</p>
          </div>
          <button
            onClick={request}
            className="shrink-0 rounded-lg bg-brand px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-brand-dark"
          >
            Enable
          </button>
        </div>
      )}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}
      <DinacharyaCard
        routine={routine}
        weather={weather}
        weatherLoading={weatherStatus === "loading"}
        onRefreshWeather={refetchWeather}
        loading={status === "loading"}
        onRegenerate={regenerate}
      />
    </div>
  );
}
