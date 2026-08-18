import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const guardrailsApi = {
  check: (payload) => request(endpoints.guardrails.check, { method: "POST", body: payload }),
  interactions: (herb) => request(endpoints.guardrails.interactions(herb)),
};
