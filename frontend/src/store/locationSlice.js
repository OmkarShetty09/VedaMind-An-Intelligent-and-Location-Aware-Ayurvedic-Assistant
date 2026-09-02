import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { authApi } from "../api/auth.js";
import { weatherApi } from "../api/weather.js";

export const saveLocation = createAsyncThunk("location/save", async ({ lat, lon }) => {
  const data = await authApi.updateLocation(lat, lon);
  return data;
});

export const fetchWeather = createAsyncThunk("location/weather", async () => {
  const data = await weatherApi.current();
  return data;
});

const locationSlice = createSlice({
  name: "location",
  initialState: {
    coords: null,
    weather: null,
    permission: "unknown",
    status: "idle",
    error: null,
  },
  reducers: {
    setCoords(state, action) {
      state.coords = action.payload;
      state.permission = "granted";
    },
    setPermission(state, action) {
      state.permission = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchWeather.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchWeather.fulfilled, (state, action) => {
        state.weather = action.payload;
        state.status = "done";
      })
      .addCase(fetchWeather.rejected, (state, action) => {
        state.status = "idle";
        state.error = action.error.message;
      })
      .addCase(saveLocation.rejected, (state, action) => {
        state.error = action.error.message;
      });
  },
});

export const { setCoords, setPermission } = locationSlice.actions;
export default locationSlice.reducer;
