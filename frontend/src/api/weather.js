import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const weatherApi = {
  current: () => request(endpoints.weather),
};
