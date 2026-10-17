import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { chatApi } from "../api/chat.js";

export const listSessions = createAsyncThunk("chat/sessions", async () => chatApi.listSessions());
export const loadSession = createAsyncThunk("chat/loadSession", async (id) => chatApi.getSession(id));
export const deleteSession = createAsyncThunk("chat/deleteSession", async (id) => {
  await chatApi.deleteSession(id);
  return id;
});

const META_KEYS = ["citations", "blocked", "low_confidence", "context_chip", "guardrail", "clarifying_question"];

/**
 * The assistant message for the turn in flight. Guardrail / citation / chip events arrive before
 * (or instead of) any tokens, so the message is created on the first event of the turn.
 */
function currentAssistant(state) {
  const last = state.messages[state.messages.length - 1];
  if (last && last.role === "assistant" && last.streaming) return last;
  const fresh = { role: "assistant", content: "", streaming: true };
  state.messages.push(fresh);
  return state.messages[state.messages.length - 1];
}

function applyMeta(message, meta = {}) {
  for (const key of META_KEYS) {
    if (meta[key] !== undefined && meta[key] !== null && meta[key] !== false) message[key] = meta[key];
  }
}

/** Server history rows -> the shape MessageBubble renders. */
function fromServer(m) {
  return {
    id: m.id,
    role: m.role,
    content: m.content || "",
    citations: m.source_citations || [],
    blocked: Boolean(m.block_reason) && !m.content,
    block_reason: m.block_reason || "",
  };
}

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    sessions: [],
    activeSessionId: null,
    messages: [],
    streaming: false,
    error: null,
    retryState: null,
  },
  reducers: {
    setSession(state, action) {
      state.activeSessionId = action.payload;
    },
    startStream(state) {
      state.streaming = true;
      state.error = null;
      state.retryState = null;
    },
    appendUserMessage(state, action) {
      state.messages.push({ role: "user", content: action.payload });
      state.streaming = true;
    },
    appendAssistantChunk(state, action) {
      const message = currentAssistant(state);
      message.content = (message.content || "") + action.payload;
    },
    updateAssistantMessage(state, action) {
      applyMeta(currentAssistant(state), action.payload);
    },
    finishAssistantMessage(state, action) {
      const message = currentAssistant(state);
      applyMeta(message, action.payload);
      message.question = action.payload?.question;
      message.streaming = false;
      state.streaming = false;
    },
    setStreamError(state, action) {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === "assistant" && last.streaming) {
        last.streaming = false;
        // Nothing was produced for this turn: drop the empty bubble, the error banner explains it.
        if (!last.content && !last.guardrail && !last.clarifying_question) state.messages.pop();
      }
      state.error = action.payload;
      state.streaming = false;
      state.retryState = null;
    },
    setRetryState(state, action) {
      state.retryState = action.payload;
    },
    clearRetryState(state) {
      state.retryState = null;
    },
    clearMessages(state) {
      state.messages = [];
      state.activeSessionId = null;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(listSessions.fulfilled, (state, action) => {
        state.sessions = action.payload?.results || action.payload || [];
      })
      .addCase(loadSession.fulfilled, (state, action) => {
        state.activeSessionId = action.payload.id;
        state.messages = (action.payload.messages || []).map(fromServer);
        state.error = null;
      })
      .addCase(loadSession.rejected, (state, action) => {
        state.error = action.error.message;
      })
      .addCase(deleteSession.fulfilled, (state, action) => {
        state.sessions = state.sessions.filter((s) => s.id !== action.payload);
        if (state.activeSessionId === action.payload) {
          state.activeSessionId = null;
          state.messages = [];
        }
      });
  },
});

export const {
  setSession,
  startStream,
  appendUserMessage,
  appendAssistantChunk,
  updateAssistantMessage,
  finishAssistantMessage,
  setStreamError,
  setRetryState,
  clearRetryState,
  clearMessages,
} = chatSlice.actions;
export default chatSlice.reducer;
