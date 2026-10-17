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
    saved: false, // coords stored on the server for the signed-in user (weather + routine use them)
  },
  reducers: {
    setCoords(state, action) {
      const prev = state.coords;
      if (!prev || prev.lat !== action.payload.lat || prev.lon !== action.payload.lon) state.saved = false;
      state.coords = action.payload;
      state.permission = "granted";
    },
    // A city the user picked by name: already saved on the server, so don't re-save it as GPS.
    setManualLocation(state, action) {
      state.coords = action.payload;
      state.saved = true;
      state.permission = "manual";
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
      .addCase(saveLocation.pending, (state) => {
        state.saved = true; // set early so a re-render doesn't send a second save
      })
      .addCase(saveLocation.rejected, (state, action) => {
        state.saved = false;
        state.error = action.error.message;
      });
  },
});

export const { setCoords, setManualLocation, setPermission } = locationSlice.actions;
export default locationSlice.reducer;
