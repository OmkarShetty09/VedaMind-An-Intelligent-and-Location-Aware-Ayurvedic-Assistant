import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { doshaApi } from "../api/dosha.js";

export const submitQuiz = createAsyncThunk("dosha/quiz", async (answers) => {
  const data = await doshaApi.submitQuiz(answers);
  return data;
});

export const loadProfile = createAsyncThunk("dosha/profile", async () => {
  const data = await doshaApi.getProfile();
  return data;
});

const doshaSlice = createSlice({
  name: "dosha",
  initialState: {
    result: null,
    profile: null,
    status: "idle",
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(submitQuiz.pending, (state) => {
        state.status = "loading";
      })
      .addCase(submitQuiz.fulfilled, (state, action) => {
        state.status = "done";
        state.result = action.payload;
      })
      .addCase(submitQuiz.rejected, (state, action) => {
        state.status = "idle";
        state.error = action.error.message;
      })
      .addCase(loadProfile.fulfilled, (state, action) => {
        state.profile = action.payload;
      });
  },
});

export default doshaSlice.reducer;
