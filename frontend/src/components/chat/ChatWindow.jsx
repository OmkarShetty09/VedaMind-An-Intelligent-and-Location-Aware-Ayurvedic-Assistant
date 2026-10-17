import { useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link } from "react-router-dom";

import request from "../../api/client.js";
import { endpoints } from "../../api/endpoints.js";
import { useChat } from "../../hooks/useChat.js";
import { deleteSession, listSessions, loadSession } from "../../store/chatSlice.js";
import { DisclaimerInline } from "./DisclaimerInline.jsx";
import { GuardrailWarningBanner } from "./GuardrailWarningBanner.jsx";
import { MessageBubble } from "./MessageBubble.jsx";
import { MessageInput } from "./MessageInput.jsx";
import { RetrievalProgress } from "./RetrievalProgress.jsx";


function SessionHistory({ onClose }) {
  const dispatch = useDispatch();
  const { sessions, activeSessionId } = useSelector((s) => s.chat);

  useEffect(() => {
    dispatch(listSessions());
  }, [dispatch]);

  if (!sessions.length) {
    return <p className="px-4 py-3 text-xs text-text-muted">No saved conversations yet.</p>;
  }
  return (
    <ul className="max-h-64 divide-y divide-line overflow-y-auto">
      {sessions.map((s) => (
        <li key={s.id} className="flex items-center gap-2 px-4 py-2">
          <button
            onClick={() => {
              dispatch(loadSession(s.id));
              onClose();
            }}
            className={`flex-1 truncate text-left text-sm hover:text-brand ${
              s.id === activeSessionId ? "font-semibold text-brand" : "text-text"
            }`}
            title={s.title || "Conversation"}
          >
            {s.title || "Conversation"}
            <span className="ml-2 text-[11px] font-normal text-text-faint">
              {new Date(s.updated_at).toLocaleString()}
            </span>
          </button>
          <button
            onClick={() => dispatch(deleteSession(s.id))}
            className="rounded px-2 py-0.5 text-[11px] text-text-faint hover:bg-red-50 hover:text-red-700"
            aria-label="Delete conversation"
          >
            Delete
          </button>
        </li>
      ))}
    </ul>
  );
}

export function ChatWindow() {
  const { messages, streaming, error, retryState, send, newChat } = useChat();
  const bottomRef = useRef(null);
  const [showHistory, setShowHistory] = useState(false);
  // Starter questions are managed in the admin (ChatSuggestion).
  const [suggestions, setSuggestions] = useState([]);

  useEffect(() => {
    request(endpoints.chat.suggestions)
      .then((data) => setSuggestions(data?.results || []))
      .catch(() => setSuggestions([]));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const lastMessage = messages[messages.length - 1];
  const pendingClarification =
    lastMessage?.role === "assistant" && lastMessage.clarifying_question ? lastMessage : null;

  return (
    <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-line bg-surface shadow-soft">
      <div className="flex items-center justify-end gap-2 border-b border-line px-4 py-2">
        <button
          onClick={() => setShowHistory((v) => !v)}
          className="rounded-lg px-3 py-1 text-xs font-medium text-text-muted transition-colors hover:bg-brand-50 hover:text-brand"
        >
          {showHistory ? "Hide history" : "History"}
        </button>
        <button
          onClick={() => {
            newChat();
            setShowHistory(false);
          }}
          disabled={streaming}
          className="rounded-lg px-3 py-1 text-xs font-medium text-text-muted transition-colors hover:bg-brand-50 hover:text-brand disabled:opacity-50"
        >
          New chat
        </button>
      </div>
      {showHistory && (
        <div className="border-b border-line bg-surface-warm">
          <SessionHistory onClose={() => setShowHistory(false)} />
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 && !streaming && (
          <div className="flex h-full flex-col items-center justify-center px-6 py-12 text-center">
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-2xl">
              🌿
            </div>
            <h2 className="text-lg font-semibold text-text">How can VedaMind help?</h2>
            <p className="mt-2 max-w-sm text-sm leading-relaxed text-text-muted">
              Ask about Ayurvedic herbs, daily routines, seasonal living, food, or classical Ayurvedic concepts.
            </p>
            <div className="mt-6 flex max-w-md flex-wrap justify-center gap-2">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-xl border border-line bg-white px-4 py-2 text-xs font-medium text-text-muted transition-all duration-150 hover:border-brand/30 hover:bg-brand-50 hover:text-brand-800"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.length > 0 && (
          <div className="space-y-4 p-4">
            {messages.map((m, i) => (
              <div key={m.id || i}>
                {m.role === "assistant" && m.guardrail && <GuardrailWarningBanner decision={m.guardrail} />}
                <MessageBubble message={m} />
              </div>
            ))}
            {streaming && <RetrievalProgress streaming={streaming} />}
            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {pendingClarification && !streaming && (
        <div className="border-t border-line px-4 py-3">
          <div className="flex flex-wrap gap-2">
            <Link
              to="/profile"
              className="rounded-xl border border-line bg-white px-4 py-2 text-xs font-medium text-text transition-all duration-150 hover:border-brand/30 hover:bg-brand-50"
            >
              Yes — add my medications/conditions
            </Link>
            <button
              onClick={() =>
                send(
                  pendingClarification.question
                    ? `I don't take any medication and have no diagnosed condition. ${pendingClarification.question}`
                    : "I don't take any medication and have no diagnosed condition."
                )
              }
              className="rounded-xl border border-line bg-white px-4 py-2 text-xs font-medium text-text transition-all duration-150 hover:border-brand/30 hover:bg-brand-50"
            >
              No medication — please answer
            </button>
          </div>
        </div>
      )}

      {retryState && (
        <div className="border-t border-amber-200 bg-amber-50 px-4 py-2.5 text-xs text-amber-700">
          Rate limited — retrying in {retryState.nextRetryIn}s (attempt {retryState.attempt}/3)
        </div>
      )}

      <MessageInput onSend={send} disabled={streaming || !!retryState} />

      <div className="border-t border-line px-4 py-2">
        <DisclaimerInline />
      </div>
    </div>
  );
}
