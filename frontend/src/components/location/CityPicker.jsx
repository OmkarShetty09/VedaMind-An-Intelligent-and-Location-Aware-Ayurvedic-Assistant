import { useState } from "react";
import { useDispatch } from "react-redux";

import { authApi } from "../../api/auth.js";
import request from "../../api/client.js";
import { endpoints } from "../../api/endpoints.js";
import { fetchWeather, setManualLocation } from "../../store/locationSlice.js";

/** Search a city by name and save it as the user's location (for when browser geolocation is blocked). */
export function CityPicker({ onSaved }) {
  const dispatch = useDispatch();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const search = async (e) => {
    e.preventDefault();
    if (query.trim().length < 2) return;
    setBusy(true);
    setError(null);
    try {
      const data = await request(`${endpoints.places}?q=${encodeURIComponent(query.trim())}`);
      setResults(data?.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const choose = async (place) => {
    setBusy(true);
    setError(null);
    try {
      await authApi.updateLocation(place.lat, place.lon, { source: "user", place_name: place.label });
      dispatch(setManualLocation({ lat: place.lat, lon: place.lon }));
      dispatch(fetchWeather());
      setResults(null);
      setQuery("");
      onSaved?.(place);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-2">
      <form onSubmit={search} className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Type your city, e.g. Bengaluru"
          aria-label="City"
          className="flex-1 rounded-lg border border-line bg-white px-3 py-1.5 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/10"
        />
        <button
          type="submit"
          disabled={busy || query.trim().length < 2}
          className="shrink-0 rounded-lg bg-brand px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-dark disabled:opacity-50"
        >
          {busy ? "..." : "Search"}
        </button>
      </form>
      {error && <p className="text-xs text-red-700">{error}</p>}
      {results && results.length === 0 && <p className="text-xs text-text-muted">No matching city found.</p>}
      {results && results.length > 0 && (
        <ul className="divide-y divide-line rounded-lg border border-line bg-white">
          {results.map((place) => (
            <li key={`${place.lat},${place.lon}`}>
              <button
                type="button"
                onClick={() => choose(place)}
                disabled={busy}
                className="w-full px-3 py-2 text-left text-sm hover:bg-brand-50"
              >
                <span className="font-medium text-text">{place.name}</span>
                <span className="ml-2 text-xs text-text-muted">{place.region}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
