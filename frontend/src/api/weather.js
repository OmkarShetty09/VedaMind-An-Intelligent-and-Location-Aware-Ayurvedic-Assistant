import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const weatherApi = {
  current: async () => {
    const raw = await request(endpoints.weather);
    const current = raw?.payload?.current || {};
    return {
      temp_c: current.temp ?? null,
      humidity: current.humidity ?? null,
      condition: current.weather?.[0]?.description || null,
    };
  },
};
