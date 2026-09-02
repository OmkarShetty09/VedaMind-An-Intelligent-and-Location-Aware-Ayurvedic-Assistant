import { useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { saveLocation, setCoords, setPermission } from "../store/locationSlice.js";
import { getAccessToken } from "../api/client.js";

export function useGeolocation({ autoRequest = true, persist = true } = {}) {
  const dispatch = useDispatch();
  const { coords, permission } = useSelector((s) => s.location);

  const request = useCallback(() => {
    if (!("geolocation" in navigator)) {
      dispatch(setPermission("unsupported"));
      return;
    }
    dispatch(setPermission("prompt"));
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const next = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        dispatch(setCoords(next));
        if (persist && getAccessToken()) dispatch(saveLocation(next));
      },
      () => dispatch(setPermission("denied")),
      { enableHighAccuracy: false, timeout: 10_000, maximumAge: 600_000 }
    );
  }, [dispatch, persist]);

  useEffect(() => {
    if (autoRequest && permission === "unknown") request();
  }, [autoRequest, permission, request]);

  return { coords, permission, request };
}
