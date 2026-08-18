export const API_BASE = "/api/v1";

export const endpoints = {
  auth: {
    register: `${API_BASE}/auth/register/`,
    login: `${API_BASE}/auth/login/`,
    refresh: `${API_BASE}/auth/refresh/`,
    logout: `${API_BASE}/auth/logout/`,
    me: `${API_BASE}/auth/me/`,
    meConsent: `${API_BASE}/auth/me/consent/`,
    location: `${API_BASE}/auth/me/location/`,
  },
  dosha: {
    quiz: `${API_BASE}/dosha/quiz/`,
    profile: `${API_BASE}/dosha/profile/`,
  },
  dinacharya: `${API_BASE}/dinacharya/`,
  weather: `${API_BASE}/weather/current/`,
  guardrails: {
    check: `${API_BASE}/guardrails/check/`,
    interactions: (herb) => `${API_BASE}/guardrails/interactions/${encodeURIComponent(herb)}/`,
  },
  chat: {
    chat: `${API_BASE}/chat/`,
    sessions: `${API_BASE}/chat/sessions/`,
    session: (id) => `${API_BASE}/chat/sessions/${id}/`,
  },
  interactionsLog: `${API_BASE}/interactions-log/`,
};
