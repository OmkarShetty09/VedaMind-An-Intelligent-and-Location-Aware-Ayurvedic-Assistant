import { useCallback, useRef, useState } from "react";

import { openSSE } from "../utils/sse.js";

/**
 * Returns { connect, abort, streaming }. connect(url, body, handlers).
 * handlers: { onToken, onGuardrail, onCitation, onDone, onError }
 */
export function useSSE() {
  const [streaming, setStreaming] = useState(false);
  const controllerRef = useRef(null);

  const connect = useCallback(async (url, body, handlers) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setStreaming(true);
    try {
      await openSSE(url, {
        body,
        signal: controller.signal,
        onEvent: ({ event, data }) => {
          switch (event) {
            case "token":
              handlers.onToken?.(data.delta);
              break;
            case "guardrail":
              handlers.onGuardrail?.(data);
              break;
            case "citation":
              handlers.onCitation?.(data);
              break;
            case "done":
              handlers.onDone?.(data);
              setStreaming(false);
              break;
            case "error":
              handlers.onError?.(data);
              setStreaming(false);
              break;
            default:
              break;
          }
        },
        onError: (err) => {
          handlers.onError?.(err);
          setStreaming(false);
        },
      });
    } catch (err) {
      if (err.name !== "AbortError") handlers.onError?.({ message: err.message });
      setStreaming(false);
    }
  }, []);

  const abort = useCallback(() => {
    controllerRef.current?.abort();
    setStreaming(false);
  }, []);

  return { connect, abort, streaming };
}
