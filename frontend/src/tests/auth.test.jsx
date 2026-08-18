import { describe, expect, it } from "vitest";

import authReducer, { login } from "../store/authSlice.js";

describe("authSlice", () => {
  it("handles login pending", () => {
    const state = authReducer(undefined, login.pending());
    expect(state.status).toBe("loading");
  });

  it("handles login fulfilled", () => {
    const state = authReducer(undefined, login.fulfilled({ email: "a@b.c" }));
    expect(state.status).toBe("authenticated");
    expect(state.user.email).toBe("a@b.c");
  });

  it("handles login rejected", () => {
    const state = authReducer(undefined, login.rejected(new Error("bad creds")));
    expect(state.status).toBe("idle");
    expect(state.error).toBeTruthy();
  });
});
