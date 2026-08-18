import { useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";

import { clearError, fetchMe, login, logout, register, updateConsent } from "../store/authSlice.js";

export function useAuth() {
  const dispatch = useDispatch();
  const { user, status, consentStatus, error } = useSelector((s) => s.auth);

  useEffect(() => {
    if (status === "idle") dispatch(fetchMe());
  }, [dispatch, status]);

  const signIn = useCallback((payload) => dispatch(login(payload)), [dispatch]);
  const signUp = useCallback((payload) => dispatch(register(payload)), [dispatch]);
  const signOut = useCallback(() => dispatch(logout()), [dispatch]);
  const acceptConsent = useCallback(() => dispatch(updateConsent(true)), [dispatch]);
  const dismissError = useCallback(() => dispatch(clearError()), [dispatch]);

  return {
    user,
    isAuthenticated: status === "authenticated",
    loading: status === "loading",
    consentAccepted: Boolean(user?.consent_accepted),
    consentStatus,
    error,
    signIn,
    signUp,
    signOut,
    acceptConsent,
    dismissError,
  };
}
