import { createContext, useContext, useEffect, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";

import { useAuthContext } from "./AuthContext.jsx";
import { useGeolocation } from "../hooks/useGeolocation.js";
import { fetchWeather, saveLocation } from "../store/locationSlice.js";

const LocationContext = createContext(null);

export function LocationProvider({ children }) {
  const geo = useGeolocation();
  const dispatch = useDispatch();
  const { isAuthenticated } = useAuthContext();
  const saved = useSelector((s) => s.location.saved);

  // Location is usually granted on the login screen, before there is a session to store it in.
  useEffect(() => {
    if (isAuthenticated && geo.coords && !saved) {
      dispatch(saveLocation(geo.coords)).then(() => dispatch(fetchWeather()));
    }
  }, [dispatch, isAuthenticated, geo.coords, saved]);

  const value = useMemo(() => geo, [geo]);
  return <LocationContext.Provider value={value}>{children}</LocationContext.Provider>;
}

export function useLocationContext() {
  const ctx = useContext(LocationContext);
  if (!ctx) throw new Error("useLocationContext must be used within LocationProvider");
  return ctx;
}
