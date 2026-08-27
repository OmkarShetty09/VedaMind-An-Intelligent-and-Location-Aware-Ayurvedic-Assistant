import { useState } from "react";

export function SourceCitation({ sources }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources?.length) return null;

  const inlineRefs = sources.slice(0, 3);
  const hasMore = sources.length > 3;

  return (
    <div className="mt-2 border-t border-line pt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 text-xs font-medium text-text-muted hover:text-brand"
      >
        <span>Sources ({sources.length})</span>
        <span className="text-[10px]">{expanded ? "▲" : "▼"}</span>
      </button>
      {!expanded && (
        <div className="mt-1 flex flex-wrap gap-1">
          {inlineRefs.map((s, i) => (
            <span
              key={i}
              className="inline-flex items-center rounded bg-brand-light px-1.5 py-0.5 text-[10px] text-brand"
            >
              {s.source}
              {s.chapter ? ` ${s.chapter}` : ""}
              {s.verse ? `:${s.verse}` : ""}
            </span>
          ))}
          {hasMore && (
            <span className="text-[10px] text-text-muted">+{sources.length - 3} more</span>
          )}
        </div>
      )}
      {expanded && (
        <ul className="mt-1 space-y-1">
          {sources.map((s, i) => (
            <li key={i} className="text-xs text-text-muted">
              {s.source}
              {s.chapter ? ` · ${s.chapter}` : ""}
              {s.verse ? ` · ${s.verse}` : ""}
              <span className="ml-1 rounded bg-brand-light px-1.5 py-0.5 text-[10px] text-brand">
                {s.evidence_level}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
