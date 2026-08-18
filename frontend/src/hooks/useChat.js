import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";

import { endpoints } from "../api/endpoints.js";
import {
  appendAssistantChunk,
  appendUserMessage,
  finishAssistantMessage,
  setSession,
  setStreamError,
  startStream,
} from "../store/chatSlice.js";
import { recordDecision } from "../store/guardrailSlice.js";
import { useSSE } from "./useSSE.js";

export function useChat() {
  const dispatch = useDispatch();
  const { connect, streaming } = useSSE();
  const { messages, activeSessionId, error } = useSelector((s) => s.chat);

  const send = useCallback(
    (text, { onGuardrail } = {}) => {
      if (!text.trim()) return;
      dispatch(startStream());
      dispatch(appendUserMessage(text));
      connect(
        endpoints.chat.chat,
        { message: text, session_id: activeSessionId },
        {
          onToken: (delta) => dispatch(appendAssistantChunk(delta)),
          onGuardrail: (decision) => {
            dispatch(recordDecision(decision));
            onGuardrail?.(decision);
          },
          onCitation: (data) => {
            dispatch(finishAssistantMessage({ citations: data.sources }));
          },
          onDone: () => dispatch(finishAssistantMessage({})),
          onError: (err) => dispatch(setStreamError(err.message || "Stream failed")),
        }
      );
    },
    [connect, dispatch, activeSessionId]
  );

  const selectSession = useCallback((id) => dispatch(setSession(id)), [dispatch]);

  return { messages, streaming, error, send, selectSession };
}
