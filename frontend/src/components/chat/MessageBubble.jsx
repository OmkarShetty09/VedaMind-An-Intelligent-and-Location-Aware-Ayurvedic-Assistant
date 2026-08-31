import { SourceCitation } from "./SourceCitation.jsx";

export function MessageBubble({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] px-4 py-3 text-sm leading-relaxed sm:max-w-[75%] ${
          isUser
            ? "rounded-2xl rounded-br-md bg-brand text-white shadow-sm"
            : message.low_confidence
              ? "rounded-2xl rounded-bl-md border border-amber-200 bg-amber-50/80 text-text"
              : "rounded-2xl rounded-bl-md border border-line bg-white text-text shadow-soft"
        }`}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        {message.streaming && (
          <span className="ml-0.5 inline-block animate-pulse text-brand">|</span>
        )}
        {message.low_confidence && !message.streaming && (
          <div className="mt-2.5 border-t border-amber-200/60 pt-2 text-xs text-amber-700">
            This answer may not be fully verified against classical sources.
          </div>
        )}
        {message.context_chip && !message.streaming && (
          <div className="mt-2">
            <span className="inline-flex items-center rounded-full bg-brand/10 px-2.5 py-0.5 text-[10px] font-medium text-brand">
              {message.context_chip}
            </span>
          </div>
        )}
        {message.citations?.length > 0 && <SourceCitation sources={message.citations} />}
      </div>
    </div>
  );
}
