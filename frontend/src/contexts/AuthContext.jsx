import { createContext, useContext, useMemo } from "react";
import { useDispatch } from "react-redux";

import { useAuth } from "../hooks/useAuth.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const auth = useAuth();
  const dispatch = useDispatch();
  const value = useMemo(() => ({ ...auth, dispatch }), [auth, dispatch]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used within AuthProvider");
  return ctx;
}
