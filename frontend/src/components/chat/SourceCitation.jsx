export function SourceCitation({ sources }) {
  if (!sources?.length) return null;
  return (
    <div className="mt-2">
      <p className="text-xs font-medium text-text-muted">Sources</p>
      <ul className="mt-1 space-y-1">
        {sources.map((s, i) => (
          <li key={i} className="text-xs text-text-muted">
            {s.source}
            {s.chapter ? ` · ${s.chapter}` : ""}
            {s.verse ? ` · ${s.verse}` : ""}
            <span className="ml-1 rounded bg-brand-light px-1.5 py-0.5 text-[10px] text-brand">{s.evidence_level}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
