import { useEffect, useRef, useState } from "react";

import { useChat } from "../../hooks/useChat.js";
import { DisclaimerInline } from "./DisclaimerInline.jsx";
import { GuardrailWarningBanner } from "./GuardrailWarningBanner.jsx";
import { MessageBubble } from "./MessageBubble.jsx";
import { MessageInput } from "./MessageInput.jsx";
import { RetrievalProgress } from "./RetrievalProgress.jsx";

const SUGGESTIONS = [
  "What should my morning routine look like?",
  "Tell me about Ashwagandha",
  "What is Dinacharya?",
  "How does Ayurveda describe seasonal living?",
];

export function ChatWindow() {
  const { messages, streaming, error, retryState, send } = useChat();
  const bottomRef = useRef(null);
  const [quickReply, setQuickReply] = useState(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant");
  const lastGuardrail = lastAssistant?.guardrail;
  const lastClarifying = lastAssistant?.clarifying_question;

  const handleQuickReply = (answer) => {
    setQuickReply(null);
    send(answer);
  };

  return (
    <div className="flex flex-1 flex-col overflow-hidden rounded-2xl border border-line bg-surface shadow-soft">
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
              {SUGGESTIONS.map((s) => (
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
              <div key={i}>
                {m.role === "assistant" && m.guardrail && (
                  <GuardrailWarningBanner decision={m.guardrail} />
                )}
                <MessageBubble message={m} />
              </div>
            ))}
            {streaming && <RetrievalProgress streaming={streaming} />}
            {lastGuardrail && !["pass", "caution"].includes(lastGuardrail.decision) && (
              <GuardrailWarningBanner decision={lastGuardrail} />
            )}
            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {lastClarifying && !streaming && (
        <div className="border-t border-line px-4 py-3">
          <p className="mb-2 text-sm text-text-muted">{lastClarifying}</p>
          <div className="flex gap-2">
            <button
              onClick={() => handleQuickReply("Yes, I take medication or have a condition")}
              className="rounded-xl border border-line bg-white px-4 py-2 text-xs font-medium text-text transition-all duration-150 hover:border-brand/30 hover:bg-brand-50"
            >
              Yes, I take medication
            </button>
            <button
              onClick={() => handleQuickReply("No, I don't take any medication")}
              className="rounded-xl border border-line bg-white px-4 py-2 text-xs font-medium text-text transition-all duration-150 hover:border-brand/30 hover:bg-brand-50"
            >
              No medication
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
