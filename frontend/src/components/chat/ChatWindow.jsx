import { useEffect, useRef, useState } from "react";

import { useChat } from "../../hooks/useChat.js";
import { DisclaimerInline } from "./DisclaimerInline.jsx";
import { GuardrailWarningBanner } from "./GuardrailWarningBanner.jsx";
import { MessageBubble } from "./MessageBubble.jsx";
import { MessageInput } from "./MessageInput.jsx";
import { RetrievalProgress } from "./RetrievalProgress.jsx";

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
    <div className="flex h-[calc(100vh-12rem)] flex-col overflow-hidden rounded-2xl border border-line bg-surface">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && !streaming && (
          <div className="flex h-full items-center justify-center text-center text-sm text-text-muted">
            Ask me anything about Ayurvedic herbs, daily routines, or seasonal living.
          </div>
        )}
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
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div ref={bottomRef} />
      </div>
      {lastClarifying && !streaming && (
        <div className="border-t border-line px-4 py-3">
          <p className="mb-2 text-sm text-text-muted">{lastClarifying}</p>
          <div className="flex gap-2">
            <button
              onClick={() => handleQuickReply("Yes, I take medication or have a condition")}
              className="rounded-lg border border-line bg-white px-3 py-1.5 text-xs text-text hover:border-brand"
            >
              Yes, I take medication
            </button>
            <button
              onClick={() => handleQuickReply("No, I don't take any medication")}
              className="rounded-lg border border-line bg-white px-3 py-1.5 text-xs text-text hover:border-brand"
            >
              No medication
            </button>
          </div>
        </div>
      )}
      {retryState && (
        <div className="border-t border-line bg-amber-50 px-4 py-2 text-xs text-amber-700">
          Rate limited — retrying in {retryState.nextRetryIn}s (attempt {retryState.attempt}/3)…
        </div>
      )}
      <MessageInput onSend={send} disabled={streaming || !!retryState} />
      <div className="border-t border-line px-4 py-2">
        <DisclaimerInline />
      </div>
    </div>
  );
}
