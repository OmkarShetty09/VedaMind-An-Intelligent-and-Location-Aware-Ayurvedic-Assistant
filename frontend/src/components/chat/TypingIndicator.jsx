export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-1 py-2">
      <span className="h-2 w-2 animate-bounce rounded-full bg-brand/60" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-brand/60 [animation-delay:120ms]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-brand/60 [animation-delay:240ms]" />
    </div>
  );
}
