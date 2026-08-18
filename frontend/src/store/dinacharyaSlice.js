import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { dinacharyaApi } from "../api/dinacharya.js";

export const loadRoutine = createAsyncThunk("dinacharya/load", async () => dinacharyaApi.getRoutine());
export const regenerate = createAsyncThunk("dinacharya/regenerate", async () => dinacharyaApi.regenerate());

const dinacharyaSlice = createSlice({
  name: "dinacharya",
  initialState: {
    routine: null,
    status: "idle",
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(loadRoutine.pending, (state) => {
        state.status = "loading";
      })
      .addCase(loadRoutine.fulfilled, (state, action) => {
        state.status = "done";
        state.routine = action.payload;
      })
      .addCase(loadRoutine.rejected, (state, action) => {
        state.status = "idle";
        state.error = action.error.message;
      })
      .addCase(regenerate.fulfilled, (state, action) => {
        state.routine = action.payload;
      });
  },
});

export default dinacharyaSlice.reducer;
