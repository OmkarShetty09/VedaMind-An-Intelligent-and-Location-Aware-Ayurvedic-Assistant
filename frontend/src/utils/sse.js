import { errorMessage, getAccessToken, refreshAccessToken } from "../api/client.js";
import { endpoints } from "../api/endpoints.js";

const MAX_RETRIES = 3;

function parseRetryDelay(response, body) {
  const retryAfter = response.headers?.get("Retry-After");
  if (retryAfter) {
    const seconds = parseInt(retryAfter, 10);
    if (!isNaN(seconds)) return seconds;
  }
  const match = (body?.error?.message || body?.message)?.match?.(/available in (\d+) seconds?/);
  if (match) return parseInt(match[1], 10);
  return 5;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * POST-based SSE: fetch() gives us a ReadableStream we can read line by line.
 * Django re-wraps RAG events as `event: X\ndata: {...}\n\n` frames.
 */
export async function openSSE(url, { body, onEvent, onError, onRetry, signal }) {
  let refreshed = false;
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    const token = getAccessToken();
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
      credentials: "include",
      signal,
    });

    // Access tokens are short-lived; renew once from the refresh cookie and resend.
    if (response.status === 401 && !refreshed) {
      refreshed = true;
      if (await refreshAccessToken()) {
        attempt--;
        continue;
      }
    }

    if (response.status === 429 && attempt < MAX_RETRIES) {
      let errorBody = {};
      try {
        errorBody = await response.json();
      } catch {
        /* ignore parse error */
      }
      const delay = parseRetryDelay(response, errorBody);
      onRetry?.({ attempt: attempt + 1, nextRetryIn: delay, message: errorBody?.error?.message || "Rate limited" });
      await sleep(delay * 1000);
      continue;
    }

    if (!response.ok) {
      let message = `Stream failed (${response.status})`;
      try {
        message = errorMessage(await response.json(), response.status);
      } catch {
        /* keep default */
      }
      onError({ code: "http_" + response.status, message, status: response.status });
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
      const frames = buffer.split("\n\n");
      buffer = frames.pop();
      for (const frame of frames) {
        const event = parseFrame(frame);
        if (event) onEvent(event);
      }
    }
    const last = parseFrame(buffer + decoder.decode());
    if (last) onEvent(last);
    return;
  }
}

export function parseFrame(frame) {
  let eventName = "message";
  const dataLines = [];
  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) eventName = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }
  if (!dataLines.length) return null;
  try {
    return { event: eventName, data: JSON.parse(dataLines.join("\n")) };
  } catch {
    return { event: eventName, data: dataLines.join("\n") };
  }
}

export { endpoints };
