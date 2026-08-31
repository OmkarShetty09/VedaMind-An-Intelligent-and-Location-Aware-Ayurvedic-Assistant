import { useState } from "react";

export function SourceCitation({ sources }) {
  const [expanded, setExpanded] = useState(false);

  if (!sources?.length) return null;

  const inlineRefs = sources.slice(0, 3);
  const hasMore = sources.length > 3;

  return (
    <div className="mt-3 border-t border-line/60 pt-2.5">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs font-medium text-text-muted transition-colors hover:text-brand"
      >
        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
        </svg>
        <span>Sources ({sources.length})</span>
        <svg
          className={`h-3 w-3 transition-transform duration-150 ${expanded ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={2}
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
        </svg>
      </button>
      {!expanded && (
        <div className="mt-1.5 flex flex-wrap gap-1">
          {inlineRefs.map((s, i) => (
            <span
              key={i}
              className="inline-flex items-center rounded-md bg-brand-50 px-2 py-0.5 text-[10px] font-medium text-brand-700"
            >
              {s.source}
              {s.chapter ? ` ${s.chapter}` : ""}
              {s.verse ? `:${s.verse}` : ""}
            </span>
          ))}
          {hasMore && (
            <span className="text-[10px] text-text-faint">+{sources.length - 3} more</span>
          )}
        </div>
      )}
      {expanded && (
        <ul className="mt-1.5 space-y-1">
          {sources.map((s, i) => (
            <li key={i} className="flex items-center gap-2 text-xs text-text-muted">
              <span className="h-1 w-1 shrink-0 rounded-full bg-brand/40" />
              <span>
                {s.source}
                {s.chapter ? ` ${s.chapter}` : ""}
                {s.verse ? `:${s.verse}` : ""}
              </span>
              {s.evidence_level && (
                <span className="rounded bg-brand-50 px-1.5 py-0.5 text-[10px] font-medium text-brand-600">
                  {s.evidence_level}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
