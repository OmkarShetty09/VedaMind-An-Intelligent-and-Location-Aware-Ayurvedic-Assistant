import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";

import { endpoints } from "../api/endpoints.js";
import {
  appendAssistantChunk,
  appendUserMessage,
  clearRetryState,
  finishAssistantMessage,
  setRetryState,
  setSession,
  setStreamError,
  startStream,
} from "../store/chatSlice.js";
import { recordDecision } from "../store/guardrailSlice.js";
import { useSSE } from "./useSSE.js";

export function useChat() {
  const dispatch = useDispatch();
  const { connect, streaming } = useSSE();
  const { messages, activeSessionId, error, retryState } = useSelector((s) => s.chat);
  const { coords, weather } = useSelector((s) => s.location);
  const { profile } = useSelector((s) => s.dosha);

  const send = useCallback(
    (text, { onGuardrail, onClarifyingQuestion } = {}) => {
      if (!text.trim()) return;
      dispatch(startStream());
      dispatch(appendUserMessage(text));

      const locationContext = {};
      if (coords) {
        locationContext.lat = coords.lat;
        locationContext.lon = coords.lon;
      }
      if (weather) {
        locationContext.current_weather = {
          temp_c: weather.temp_c,
          humidity: weather.humidity,
          condition: weather.condition,
        };
      }
      if (profile) {
        locationContext.season = weather?.season || null;
      }

      const payload = { message: text, location: locationContext };
      if (activeSessionId) payload.session_id = activeSessionId;

      connect(
        endpoints.chat.chat,
        payload,
        {
          onToken: (delta) => {
            dispatch(clearRetryState());
            dispatch(appendAssistantChunk(delta));
          },
          onGuardrail: (decision) => {
            dispatch(recordDecision(decision));
            onGuardrail?.(decision);
          },
          onCitation: (data) => {
            dispatch(finishAssistantMessage({ citations: data.sources }));
          },
          onContextChip: (data) => {
            dispatch(finishAssistantMessage({ context_chip: data }));
          },
          onLowConfidence: () => {
            dispatch(finishAssistantMessage({ low_confidence: true }));
          },
          onClarifyingQuestion: (data) => {
            dispatch(finishAssistantMessage({ clarifying_question: data.question }));
            onClarifyingQuestion?.(data);
          },
          onDone: (data) => {
            if (data?.session_id && !activeSessionId) {
              dispatch(setSession(data.session_id));
            }
            dispatch(finishAssistantMessage({
              blocked: data?.blocked,
              low_confidence: data?.low_confidence,
            }));
          },
          onError: (err) => dispatch(setStreamError(err.message || "Stream failed")),
          onRetry: (info) => dispatch(setRetryState(info)),
        }
      );
    },
    [connect, dispatch, activeSessionId, coords, weather, profile]
  );

  const selectSession = useCallback((id) => dispatch(setSession(id)), [dispatch]);

  return { messages, streaming, error, retryState, send, selectSession };
}
