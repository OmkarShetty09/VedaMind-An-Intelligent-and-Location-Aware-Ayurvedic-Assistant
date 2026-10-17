import { combineReducers, configureStore } from "@reduxjs/toolkit";

import authReducer from "./authSlice.js";
import chatReducer from "./chatSlice.js";
import dinacharyaReducer from "./dinacharyaSlice.js";
import doshaReducer from "./doshaSlice.js";
import guardrailReducer from "./guardrailSlice.js";
import locationReducer from "./locationSlice.js";

const appReducer = combineReducers({
  auth: authReducer,
  chat: chatReducer,
  guardrail: guardrailReducer,
  dosha: doshaReducer,
  dinacharya: dinacharyaReducer,
  location: locationReducer,
});

// Signing out must not leave the previous user's chat, profile or routine in memory for the next login.
function rootReducer(state, action) {
  if (action.type === "auth/logout/fulfilled" || action.type === "auth/logout/rejected") {
    return appReducer({ location: { ...state.location, saved: false } }, action);
  }
  return appReducer(state, action);
}

export const store = configureStore({ reducer: rootReducer });
