import { useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { setCoords, setPermission } from "../store/locationSlice.js";

/** Reads the device position into the store. LocationProvider persists it for the signed-in user. */
export function useGeolocation({ autoRequest = true } = {}) {
  const dispatch = useDispatch();
  const { coords, permission } = useSelector((s) => s.location);

  const request = useCallback(() => {
    if (!("geolocation" in navigator)) {
      dispatch(setPermission("unsupported"));
      return;
    }
    dispatch(setPermission("prompt"));
    navigator.geolocation.getCurrentPosition(
      (pos) => dispatch(setCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude })),
      () => dispatch(setPermission("denied")),
      { enableHighAccuracy: false, timeout: 10_000, maximumAge: 600_000 }
    );
  }, [dispatch]);

  useEffect(() => {
    if (autoRequest && permission === "unknown") request();
  }, [autoRequest, permission, request]);

  return { coords, permission, request };
}
