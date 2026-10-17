import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { authApi } from "../api/auth.js";
import { setAccessToken } from "../api/client.js";

export const login = createAsyncThunk("auth/login", async (payload) => {
  const data = await authApi.login(payload);
  setAccessToken(data.access);
  return data.user;
});

export function browserTimezone() {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

export const register = createAsyncThunk("auth/register", async (payload) => {
  const data = await authApi.register({ timezone: browserTimezone(), ...payload });
  setAccessToken(data.access);
  return data.user;
});

/** The Dinacharya engine schedules in the user's timezone; keep it matched to this device. */
export const syncTimezone = createAsyncThunk("auth/syncTimezone", async (_, { getState }) => {
  const tz = browserTimezone();
  const user = getState().auth.user;
  if (!user || user.timezone === tz) return user;
  return authApi.updateMe({ timezone: tz });
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
    setUser(state, action) {
      state.user = action.payload;
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
      .addCase(register.pending, (state) => {
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.status = "authenticated";
        state.user = action.payload;
      })
      .addCase(register.rejected, (state, action) => {
        state.error = action.error.message;
      })
      .addCase(syncTimezone.fulfilled, (state, action) => {
        if (action.payload) state.user = action.payload;
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
      .addCase(logout.rejected, (state) => {
        // The token is cleared in `finally` either way, so the session is over locally.
        state.status = "idle";
        state.user = null;
      })
      .addCase(updateConsent.fulfilled, (state, action) => {
        state.consentStatus = "accepted";
        if (state.user) state.user.consent_accepted = action.payload.consent_accepted;
      });
  },
});

export const { clearError, noSession, setUser } = authSlice.actions;
export default authSlice.reducer;
