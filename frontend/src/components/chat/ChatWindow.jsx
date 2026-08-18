import { useEffect, useRef } from "react";

import { useChat } from "../../hooks/useChat.js";
import { DisclaimerInline } from "./DisclaimerInline.jsx";
import { GuardrailWarningBanner } from "./GuardrailWarningBanner.jsx";
import { MessageBubble } from "./MessageBubble.jsx";
import { MessageInput } from "./MessageInput.jsx";
import { RetrievalProgress } from "./RetrievalProgress.jsx";
import { SourceCitation } from "./SourceCitation.jsx";

export function ChatWindow() {
  const { messages, streaming, error, send } = useChat();
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const lastGuardrail = [...messages].reverse().find((m) => m.blocked);

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
            {m.role === "assistant" && m.citations?.length > 0 && <SourceCitation sources={m.citations} />}
            <MessageBubble message={m} />
          </div>
        ))}
        {streaming && <RetrievalProgress streaming={streaming} />}
        {lastGuardrail?.blocked && <GuardrailWarningBanner decision={{ decision: "block", reason_code: "blocked" }} />}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <div ref={bottomRef} />
      </div>
      <MessageInput onSend={send} disabled={streaming} />
      <div className="border-t border-line px-4 py-2">
        <DisclaimerInline />
      </div>
    </div>
  );
}
