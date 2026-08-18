import { getAccessToken } from "../api/client.js";
import { endpoints } from "../api/endpoints.js";

/**
 * POST-based SSE: fetch() gives us a ReadableStream we can read line by line.
 * Django re-wraps RAG events as `event: X\ndata: {...}\n\n` frames.
 */
export async function openSSE(url, { body, onEvent, onError, signal }) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
    body: JSON.stringify(body),
    credentials: "include",
    signal,
  });

  if (!response.ok) {
    let message = `Stream failed (${response.status})`;
    try {
      const data = await response.json();
      message = data?.error?.message || data?.message || message;
    } catch {
      /* keep default */
    }
    onError({ code: "http_" + response.status, message });
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const frames = buffer.split("\n\n");
    buffer = frames.pop();
    for (const frame of frames) {
      const event = parseFrame(frame);
      if (event) onEvent(event);
    }
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
