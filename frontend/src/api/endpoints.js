export const API_BASE = "/api/v1";

export const endpoints = {
  auth: {
    register: `${API_BASE}/auth/register`,
    login: `${API_BASE}/auth/login`,
    refresh: `${API_BASE}/auth/refresh`,
    logout: `${API_BASE}/auth/logout`,
    me: `${API_BASE}/users/me`,
    meConsent: `${API_BASE}/users/me/consent`,
    location: `${API_BASE}/users/me/location`,
  },
  dosha: {
    assess: `${API_BASE}/dosha/assess`,
    profile: `${API_BASE}/dosha/profile`,
  },
  dinacharya: {
    today: `${API_BASE}/dinacharya/today`,
    recommend: `${API_BASE}/dinacharya/recommend`,
  },
  weather: `${API_BASE}/weather/current`,
  guardrails: {
    check: `${API_BASE}/guardrails/check`,
    interactions: (herb) => `${API_BASE}/guardrails/interactions/${encodeURIComponent(herb)}`,
  },
  chat: {
    chat: `${API_BASE}/chat/`,
    sessions: `${API_BASE}/chat/sessions`,
    session: (id) => `${API_BASE}/chat/sessions/${id}`,
  },
  interactionsLog: `${API_BASE}/interactions-log/`,
};
