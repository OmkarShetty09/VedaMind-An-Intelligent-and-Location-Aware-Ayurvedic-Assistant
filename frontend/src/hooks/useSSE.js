import { useCallback, useRef, useState } from "react";

import { openSSE } from "../utils/sse.js";

/**
 * Returns { connect, abort, streaming }. connect(url, body, handlers).
 * handlers: { onToken, onGuardrail, onCitation, onContextChip, onLowConfidence,
 *             onClarifyingQuestion, onDone, onError, onRetry }
 */
export function useSSE() {
  const [streaming, setStreaming] = useState(false);
  const controllerRef = useRef(null);

  const connect = useCallback(async (url, body, handlers) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setStreaming(true);
    let finished = false;
    try {
      await openSSE(url, {
        body,
        signal: controller.signal,
        onRetry: handlers.onRetry,
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
            case "context_chip":
              handlers.onContextChip?.(data);
              break;
            case "low_confidence":
              handlers.onLowConfidence?.(data);
              break;
            case "clarifying_question":
              handlers.onClarifyingQuestion?.(data);
              break;
            case "done":
              finished = true;
              handlers.onDone?.(data);
              break;
            case "error":
              finished = true;
              handlers.onError?.(data);
              break;
            default:
              break;
          }
        },
        onError: (err) => {
          finished = true;
          handlers.onError?.(err);
        },
      });
      if (!finished && !controller.signal.aborted) {
        handlers.onError?.({ message: "The answer stream ended unexpectedly. Please try again." });
      }
    } catch (err) {
      if (err.name !== "AbortError") {
        handlers.onError?.({ message: "Could not reach the server. Is the backend running?" });
      }
    } finally {
      if (controllerRef.current === controller) setStreaming(false);
    }
  }, []);

  const abort = useCallback(() => {
    controllerRef.current?.abort();
    setStreaming(false);
  }, []);

  return { connect, abort, streaming };
}
