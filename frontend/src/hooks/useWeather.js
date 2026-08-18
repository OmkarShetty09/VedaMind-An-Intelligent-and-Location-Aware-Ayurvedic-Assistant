import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { fetchWeather } from "../store/locationSlice.js";

export function useWeather({ enabled = true } = {}) {
  const dispatch = useDispatch();
  const { weather, status, error, coords } = useSelector((s) => s.location);

  useEffect(() => {
    if (enabled && coords) dispatch(fetchWeather());
  }, [enabled, coords, dispatch]);

  return { weather, status, error, coords };
}
