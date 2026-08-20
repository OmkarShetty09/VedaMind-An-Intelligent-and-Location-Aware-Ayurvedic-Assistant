import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const dinacharyaApi = {
  getRoutine: () => request(endpoints.dinacharya.today),
  regenerate: () => request(endpoints.dinacharya.recommend),
};
