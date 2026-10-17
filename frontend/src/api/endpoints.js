export const API_BASE = "/api/v1";

export const endpoints = {
  auth: {
    register: `${API_BASE}/auth/register`,
    login: `${API_BASE}/auth/login`,
    refresh: `${API_BASE}/auth/refresh`,
    logout: `${API_BASE}/auth/logout`,
    me: `${API_BASE}/users/me`,
    medications: `${API_BASE}/users/me/medications`,
    conditions: `${API_BASE}/users/me/conditions`,
    meConsent: `${API_BASE}/users/me/consent`,
    location: `${API_BASE}/users/me/location`,
  },
  dosha: {
    assess: `${API_BASE}/dosha/assess`,
    profile: `${API_BASE}/dosha/profile`,
    quiz: `${API_BASE}/dosha/quiz`,
  },
  dinacharya: {
    today: `${API_BASE}/dinacharya/today`,
    recommend: `${API_BASE}/dinacharya/recommend`,
  },
  weather: `${API_BASE}/weather/current`,
  places: `${API_BASE}/weather/places`,
  season: `${API_BASE}/dinacharya/season`,
  guardrails: {
    check: `${API_BASE}/guardrails/check`,
    interactions: (herb) => `${API_BASE}/guardrails/interactions/${encodeURIComponent(herb)}`,
  },
  chat: {
    chat: `${API_BASE}/chat/`,
    sessions: `${API_BASE}/chat/sessions`,
    session: (id) => `${API_BASE}/chat/sessions/${id}`,
    suggestions: `${API_BASE}/chat/suggestions`,
  },
  interactionsLog: `${API_BASE}/interactions-log/`,
};
