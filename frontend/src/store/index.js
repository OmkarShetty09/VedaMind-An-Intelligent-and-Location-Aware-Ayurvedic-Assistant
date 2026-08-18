import { configureStore } from "@reduxjs/toolkit";

import authReducer from "./authSlice.js";
import chatReducer from "./chatSlice.js";
import dinacharyaReducer from "./dinacharyaSlice.js";
import doshaReducer from "./doshaSlice.js";
import guardrailReducer from "./guardrailSlice.js";
import locationReducer from "./locationSlice.js";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chat: chatReducer,
    guardrail: guardrailReducer,
    dosha: doshaReducer,
    dinacharya: dinacharyaReducer,
    location: locationReducer,
  },
});
