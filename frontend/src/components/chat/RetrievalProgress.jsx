export function RetrievalProgress({ streaming }) {
  if (!streaming) return null;
  return (
    <div className="flex items-center gap-2 text-xs text-text-muted">
      <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-brand" />
      Retrieving classical sources and checking interactions...
    </div>
  );
}
