import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const weatherApi = {
  current: async () => {
    const raw = await request(endpoints.weather);
    const current = raw?.payload?.current || {};
    return {
      location_name: raw?.location_name || null,
      temp_c: current.temp ?? null,
      humidity: current.humidity ?? null,
      condition: current.weather?.[0]?.description || null,
      feels_like: current.feels_like ?? null,
      wind_speed: current.wind_speed ?? null,
      wind_direction: current.wind_direction ?? null,
      wind_gusts: current.wind_gusts ?? null,
      pressure: current.pressure ?? null,
      cloud_cover: current.cloud_cover ?? null,
      precipitation: current.precipitation ?? null,
      uv_index: current.uv_index ?? null,
      visibility: current.visibility ?? null,
      dew_point: current.dew_point ?? null,
    };
  },
};
