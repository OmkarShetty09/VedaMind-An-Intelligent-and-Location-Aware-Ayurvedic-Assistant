import { createSlice } from "@reduxjs/toolkit";

const guardrailSlice = createSlice({
  name: "guardrail",
  initialState: {
    lastDecision: null,
    history: [],
  },
  reducers: {
    recordDecision(state, action) {
      state.lastDecision = action.payload;
      state.history = [...state.history.slice(-19), action.payload];
    },
    clear(state) {
      state.lastDecision = null;
      state.history = [];
    },
  },
});

export const { recordDecision, clear } = guardrailSlice.actions;
export default guardrailSlice.reducer;
