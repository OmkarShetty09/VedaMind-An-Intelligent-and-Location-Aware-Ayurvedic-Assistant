import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { dinacharyaApi } from "../api/dinacharya.js";

export const loadRoutine = createAsyncThunk("dinacharya/load", async () => {
  try {
    return await dinacharyaApi.getRoutine();
  } catch (err) {
    if (err?.status === 404 || err?.status === 401) return null;
    throw err;
  }
});
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
        state.status = "error";
        state.error = action.error.message;
      })
      .addCase(regenerate.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(regenerate.fulfilled, (state, action) => {
        state.status = "done";
        state.routine = action.payload;
      })
      .addCase(regenerate.rejected, (state, action) => {
        state.status = "error";
        state.error = action.error.message;
      });
  },
});

export default dinacharyaSlice.reducer;
