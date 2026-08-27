import { SourceCitation } from "./SourceCitation.jsx";

export function MessageBubble({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "rounded-br-sm bg-brand text-white"
            : message.low_confidence
              ? "rounded-bl-sm border border-amber-200 bg-amber-50 text-text"
              : "rounded-bl-sm border border-line bg-surface text-text"
        }`}
      >
        {message.content}
        {message.streaming && <span className="ml-1 inline-block animate-pulse">▍</span>}
        {message.low_confidence && !message.streaming && (
          <div className="mt-2 border-t border-amber-200 pt-2 text-xs text-amber-700">
            This answer may not be fully verified against classical sources.
          </div>
        )}
        {message.context_chip && !message.streaming && (
          <div className="mt-2 flex items-center gap-2">
            <span className="inline-flex items-center rounded-full bg-brand-light px-2 py-0.5 text-[10px] font-medium text-brand">
              {message.context_chip}
            </span>
          </div>
        )}
        {message.citations?.length > 0 && <SourceCitation sources={message.citations} />}
      </div>
    </div>
  );
}
