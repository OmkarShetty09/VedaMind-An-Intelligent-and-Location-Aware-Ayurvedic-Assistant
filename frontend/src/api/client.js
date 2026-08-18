import { endpoints } from "./endpoints.js";

const ACCESS_TOKEN_KEY = "vedamind_access";

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setAccessToken(token) {
  if (token) localStorage.setItem(ACCESS_TOKEN_KEY, token);
  else localStorage.removeItem(ACCESS_TOKEN_KEY);
}

export async function request(url, { method = "GET", body, headers = {}, isForm = false } = {}) {
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

  if (response.status === 401 && url !== endpoints.auth.refresh) {
    setAccessToken(null);
    const refreshed = await tryRefresh();
    if (refreshed) return request(url, { method, body, headers, isForm });
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
    const err = new Error(data?.message || data?.error?.message || `Request failed (${response.status})`);
    err.status = response.status;
    err.data = data;
    throw err;
  }
  return data;
}

async function tryRefresh() {
  try {
    const response = await fetch(endpoints.auth.refresh, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
      credentials: "include",
    });
    if (!response.ok) return false;
    const data = await response.json();
    setAccessToken(data.access);
    return true;
  } catch {
    return false;
  }
}

export default request;
