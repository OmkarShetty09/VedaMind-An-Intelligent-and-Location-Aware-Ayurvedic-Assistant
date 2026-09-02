import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { authApi } from "../api/auth.js";
import { setAccessToken } from "../api/client.js";

export const login = createAsyncThunk("auth/login", async (payload) => {
  const data = await authApi.login(payload);
  setAccessToken(data.access);
  return data.user;
});

export const register = createAsyncThunk("auth/register", async (payload) => {
  const data = await authApi.register(payload);
  setAccessToken(data.access);
  return data.user;
});

export const fetchMe = createAsyncThunk("auth/me", async () => {
  const data = await authApi.me();
  return data;
});

export const logout = createAsyncThunk("auth/logout", async () => {
  try {
    await authApi.logout();
  } finally {
    setAccessToken(null);
  }
});

export const updateConsent = createAsyncThunk("auth/consent", async (accepted) => {
  const data = await authApi.updateConsent(accepted);
  return data;
});

const authSlice = createSlice({
  name: "auth",
  initialState: {
    user: null,
    status: "idle",
    consentStatus: "idle",
    error: null,
  },
  reducers: {
    clearError(state) {
      state.error = null;
    },
    noSession(state) {
      state.status = "anonymous";
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.status = "authenticated";
        state.user = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.status = "idle";
        state.error = action.error.message;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.status = "authenticated";
        state.user = action.payload;
      })
      .addCase(fetchMe.fulfilled, (state, action) => {
        state.status = "authenticated";
        state.user = action.payload;
      })
      .addCase(fetchMe.rejected, (state) => {
        state.status = "anonymous";
        state.user = null;
      })
      .addCase(logout.fulfilled, (state) => {
        state.status = "idle";
        state.user = null;
      })
      .addCase(updateConsent.fulfilled, (state, action) => {
        state.consentStatus = "accepted";
        if (state.user) state.user.consent_accepted = action.payload.consent_accepted;
      });
  },
});

export const { clearError, noSession } = authSlice.actions;
export default authSlice.reducer;
