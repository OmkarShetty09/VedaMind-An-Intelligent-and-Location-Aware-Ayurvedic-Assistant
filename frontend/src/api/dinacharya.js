import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const dinacharyaApi = {
  getRoutine: () => request(endpoints.dinacharya),
  regenerate: () => request(endpoints.dinacharya, { method: "POST" }),
};
