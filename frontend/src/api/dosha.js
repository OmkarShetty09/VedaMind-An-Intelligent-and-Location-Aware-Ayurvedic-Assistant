import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const doshaApi = {
  submitQuiz: (answers) => request(endpoints.dosha.assess, { method: "POST", body: { answers } }),
  getProfile: () => request(endpoints.dosha.profile),
};
