export function MessageBubble({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "rounded-br-sm bg-brand text-white"
            : "rounded-bl-sm border border-line bg-surface text-text"
        }`}
      >
        {message.content}
        {message.streaming && <span className="ml-1 inline-block animate-pulse">▍</span>}
        {message.citations?.length > 0 && (
          <div className="mt-2 border-t border-line pt-2 text-xs text-text-muted">
            Sources: {message.citations.map((c) => c.source).join(", ")}
          </div>
        )}
      </div>
    </div>
  );
}
