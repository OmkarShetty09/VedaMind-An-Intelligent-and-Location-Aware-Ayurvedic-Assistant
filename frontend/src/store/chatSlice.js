import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { chatApi } from "../api/chat.js";

export const listSessions = createAsyncThunk("chat/sessions", async () => chatApi.listSessions());
export const loadSession = createAsyncThunk("chat/loadSession", async (id) => chatApi.getSession(id));
export const deleteSession = createAsyncThunk("chat/deleteSession", async (id) => {
  await chatApi.deleteSession(id);
  return id;
});

const chatSlice = createSlice({
  name: "chat",
  initialState: {
    sessions: [],
    activeSessionId: null,
    messages: [],
    streaming: false,
    error: null,
  },
  reducers: {
    setSession(state, action) {
      state.activeSessionId = action.payload;
    },
    startStream(state) {
      state.streaming = true;
      state.error = null;
    },
    appendUserMessage(state, action) {
      state.messages.push({ role: "user", content: action.payload });
      state.streaming = true;
    },
    appendAssistantChunk(state, action) {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === "assistant" && last.streaming) {
        last.content = (last.content || "") + action.payload;
      } else {
        state.messages.push({ role: "assistant", content: action.payload, streaming: true });
      }
    },
    finishAssistantMessage(state, action) {
      const last = state.messages[state.messages.length - 1];
      if (last && last.role === "assistant") {
        last.streaming = false;
        if (action.payload?.citations) last.citations = action.payload.citations;
        if (action.payload?.blocked) last.blocked = true;
        if (action.payload?.low_confidence) last.low_confidence = true;
        if (action.payload?.context_chip) last.context_chip = action.payload.context_chip;
        if (action.payload?.guardrail) last.guardrail = action.payload.guardrail;
        if (action.payload?.clarifying_question) last.clarifying_question = action.payload.clarifying_question;
      }
      state.streaming = false;
    },
    setStreamError(state, action) {
      state.error = action.payload;
      state.streaming = false;
    },
    clearMessages(state) {
      state.messages = [];
      state.activeSessionId = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(listSessions.fulfilled, (state, action) => {
        state.sessions = action.payload.results || action.payload;
      })
      .addCase(loadSession.fulfilled, (state, action) => {
        state.activeSessionId = action.payload.id;
        state.messages = action.payload.messages || [];
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
  finishAssistantMessage,
  setStreamError,
  clearMessages,
} = chatSlice.actions;
export default chatSlice.reducer;
