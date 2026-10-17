import { endpoints } from "./endpoints.js";

const ACCESS_TOKEN_KEY = "vedamind_access";

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token) {
  if (token) localStorage.setItem(ACCESS_TOKEN_KEY, token);
  else localStorage.removeItem(ACCESS_TOKEN_KEY);
}

/** Human-readable message from the backend's {error: {code, message, fields}} envelope. */
export function errorMessage(data, status) {
  const err = data?.error;
  if (err?.message) return err.message;
  const fields = err?.fields || (data && typeof data === "object" ? data : null);
  if (fields && typeof fields === "object") {
    const parts = Object.entries(fields)
      .filter(([, v]) => v)
      .map(([k, v]) => {
        const text = Array.isArray(v) ? v.join(" ") : typeof v === "object" ? JSON.stringify(v) : String(v);
        return k === "non_field_errors" || k === "detail" ? text : `${k}: ${text}`;
      });
    if (parts.length) return parts.join(" ");
  }
  if (typeof data?.message === "string") return data.message;
  return `Request failed (${status})`;
}

export async function request(url, { method = "GET", body, headers = {}, isForm = false, _retried = false } = {}) {
  const token = getAccessToken();
  const finalHeaders = { ...headers };
  if (token) finalHeaders.Authorization = `Bearer ${token}`;
  if (body !== undefined && !isForm) finalHeaders["Content-Type"] = "application/json";

  const response = await fetch(url, {
    method,
    headers: finalHeaders,
    body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
    credentials: "include",
  });

  if (response.status === 401 && !_retried && url !== endpoints.auth.refresh && url !== endpoints.auth.login) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return request(url, { method, body, headers, isForm, _retried: true });
  }

  let data = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!response.ok) {
    const err = new Error(errorMessage(data, response.status));
    err.status = response.status;
    err.data = data;
    throw err;
  }
  return data;
}

let refreshInFlight = null;

/**
 * Exchange the refresh cookie for a new access token. Concurrent callers share one request:
 * refresh tokens rotate, so a second parallel refresh would present an already-revoked token
 * and sign the user out.
 */
export function refreshAccessToken() {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      try {
        const response = await fetch(endpoints.auth.refresh, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
          credentials: "include",
        });
        if (!response.ok) {
          setAccessToken(null);
          return false;
        }
        const data = await response.json();
        setAccessToken(data.access);
        return true;
      } catch {
        return false;
      } finally {
        refreshInFlight = null;
      }
    })();
  }
  return refreshInFlight;
}

export default request;
