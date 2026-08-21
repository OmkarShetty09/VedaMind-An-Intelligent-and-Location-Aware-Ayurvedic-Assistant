import { endpoints } from "./endpoints.js";
import request from "./client.js";

export const authApi = {
  register: (payload) => request(endpoints.auth.register, { method: "POST", body: payload }),
  login: (payload) => request(endpoints.auth.login, { method: "POST", body: payload }),
  refresh: () => request(endpoints.auth.refresh, { method: "POST", body: {} }),
  logout: () => request(endpoints.auth.logout, { method: "POST" }),
  me: () => request(endpoints.auth.me),
  updateConsent: () => request(endpoints.auth.meConsent, { method: "POST", body: { disclaimer_version: "1.0" } }),
  updateLocation: (lat, lon) =>
    request(endpoints.auth.location, { method: "POST", body: { lat, lon, source: "gps" } }),
};
