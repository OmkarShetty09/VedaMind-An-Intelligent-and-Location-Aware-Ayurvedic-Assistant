import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { getAccessToken } from "../api/client.js";
import { fetchWeather } from "../store/locationSlice.js";

export function useWeather({ enabled = true } = {}) {
  const dispatch = useDispatch();
  const { weather, status, error, coords } = useSelector((s) => s.location);

  useEffect(() => {
    if (enabled && getAccessToken()) dispatch(fetchWeather());
  }, [enabled, dispatch]);

  return { weather, status, error, coords, refetchWeather: () => dispatch(fetchWeather()) };
}
