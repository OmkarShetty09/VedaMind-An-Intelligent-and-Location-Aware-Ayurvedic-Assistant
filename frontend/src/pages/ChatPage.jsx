import { useEffect } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

import { ChatWindow } from "../components/chat/ChatWindow.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";
import { loadProfile } from "../store/doshaSlice.js";
import { store } from "../store/index.js";

export function ChatPage() {
  const navigate = useNavigate();
  const { user } = useAuthContext();
  const { profile } = useSelector((s) => s.dosha);

  useEffect(() => {
    store.dispatch(loadProfile());
  }, []);

  useEffect(() => {
    if (profile === null) return;
    if (profile && !profile.dominant_dosha) {
      navigate("/dosha", { replace: true });
    }
  }, [profile, navigate]);

  if (!profile || !profile.dominant_dosha) {
    return (
      <div className="flex h-[calc(100vh-12rem)] items-center justify-center">
        <div className="text-sm text-text-muted">Loading your profile...</div>
      </div>
    );
  }

  const doshaLabel = profile.dominant_dosha
    ? profile.dominant_dosha.charAt(0).toUpperCase() + profile.dominant_dosha.slice(1)
    : "";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-text">Ask VedaMind</h1>
          <p className="mt-1 text-sm text-text-muted">
            Grounded in classical texts, with safety checks on every answer.
          </p>
        </div>
        {doshaLabel && (
          <span className="inline-flex items-center rounded-full border border-brand bg-brand-light px-3 py-1 text-xs font-medium text-brand">
            {doshaLabel} type
          </span>
        )}
      </div>
      <ChatWindow />
    </div>
  );
}
