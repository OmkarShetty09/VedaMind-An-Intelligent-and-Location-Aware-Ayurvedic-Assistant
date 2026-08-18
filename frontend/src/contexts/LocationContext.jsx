import { createContext, useContext, useMemo } from "react";

import { useGeolocation } from "../hooks/useGeolocation.js";

const LocationContext = createContext(null);

export function LocationProvider({ children }) {
  const geo = useGeolocation();
  const value = useMemo(() => geo, [geo]);
  return <LocationContext.Provider value={value}>{children}</LocationContext.Provider>;
}

export function useLocationContext() {
  const ctx = useContext(LocationContext);
  if (!ctx) throw new Error("useLocationContext must be used within LocationProvider");
  return ctx;
}
