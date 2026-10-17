import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { ChatWindow } from "../components/chat/ChatWindow.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";
import { loadProfile } from "../store/doshaSlice.js";

export function ChatPage() {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { consentAccepted } = useAuthContext();
  const { profile, profileError } = useSelector((s) => s.dosha);

  useEffect(() => {
    dispatch(loadProfile());
  }, [dispatch]);

  useEffect(() => {
    if (profile === null) return;
    // The chat API requires both the disclaimer and a dosha profile; the assessment page handles both.
    if (!profile.dominant_dosha || !consentAccepted) {
      navigate("/dosha", { replace: true });
    }
  }, [profile, consentAccepted, navigate]);

  if (profileError && !profile) {
    return (
      <div className="flex h-[60vh] flex-col items-center justify-center gap-3 text-sm text-text-muted">
        <p>Could not load your profile: {profileError}</p>
        <button
          onClick={() => dispatch(loadProfile())}
          className="rounded-xl border border-line px-4 py-2 text-sm font-medium hover:bg-brand-50"
        >
          Try again
        </button>
      </div>
    );
  }

  if (!profile || !profile.dominant_dosha) {
    return (
      <div className="flex h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-text-muted">
          <span className="h-2 w-2 animate-pulse rounded-full bg-brand" />
          Loading your profile...
        </div>
      </div>
    );
  }

  const doshaLabel = profile.dominant_dosha.charAt(0).toUpperCase() + profile.dominant_dosha.slice(1);

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col">
      <div className="mb-3 flex items-center gap-3">
        <div>
          <h1 className="page-title">Ask VedaMind</h1>
          <p className="page-subtitle">
            Grounded in classical texts, with safety checks on every answer.
          </p>
        </div>
        <span className="shrink-0 rounded-full border border-brand/20 bg-brand-50 px-3 py-1 text-xs font-medium text-brand">
          {doshaLabel} type
        </span>
      </div>
      <ChatWindow />
    </div>
  );
}
