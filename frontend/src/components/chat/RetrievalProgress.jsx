export function RetrievalProgress({ streaming }) {
  if (!streaming) return null;
  return (
    <div className="flex items-center gap-3 rounded-xl border border-line bg-surface/80 px-4 py-3 text-xs text-text-muted">
      <div className="flex gap-1">
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand" style={{ animationDelay: "0ms" }} />
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand" style={{ animationDelay: "200ms" }} />
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-brand" style={{ animationDelay: "400ms" }} />
      </div>
      <span>Retrieving classical sources and checking interactions...</span>
    </div>
  );
}
