import { useEffect } from "react";

export function sourceLabel(s) {
  return [s.title || s.source, s.chapter].filter(Boolean).join(" · ");
}

export function sourceDomId(scope, id) {
  return `${scope}-src-${id}`;
}

function ExternalLink({ href, children }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 font-medium text-brand underline-offset-2 hover:underline"
      onClick={(e) => e.stopPropagation()}
    >
      {children}
      <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H18m0 0v4.5M18 6l-7.5 7.5M6 9v9h9" />
      </svg>
    </a>
  );
}

function hostname(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

function SourceDetails({ source }) {
  return (
    <div className="space-y-2 border-t border-line/60 px-3 py-2.5 text-xs text-text-muted">
      <dl className="grid grid-cols-[auto,1fr] gap-x-3 gap-y-0.5">
        <dt className="text-text-faint">Text</dt>
        <dd className="text-text">{source.title || source.source}</dd>
        {source.chapter && (
          <>
            <dt className="text-text-faint">Section</dt>
            <dd>{source.chapter}</dd>
          </>
        )}
        {source.verse && (
          <>
            <dt className="text-text-faint">Verse</dt>
            <dd>{source.verse}</dd>
          </>
        )}
        {source.evidence_level && (
          <>
            <dt className="text-text-faint">Evidence</dt>
            <dd className="capitalize">{source.evidence_level}</dd>
          </>
        )}
        {source.license && (
          <>
            <dt className="text-text-faint">License</dt>
            <dd>{source.license}</dd>
          </>
        )}
      </dl>
      {source.excerpt ? (
        <div>
          <p className="mb-1 font-medium text-text-faint">Passage the answer used</p>
          <blockquote className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded-lg border border-line bg-brand-50/40 px-3 py-2 leading-relaxed text-text">
            {source.excerpt}
          </blockquote>
        </div>
      ) : (
        <p className="italic text-text-faint">The passage text was not saved for this older answer.</p>
      )}
      {(source.url || source.references?.length > 0) && (
        <div className="flex flex-wrap gap-x-4 gap-y-1">
          {source.url && <ExternalLink href={source.url}>Open source ({hostname(source.url)})</ExternalLink>}
          {source.references?.map((ref) => (
            <ExternalLink key={ref} href={ref}>
              {hostname(ref)}
            </ExternalLink>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Every source is a clickable row; opening it shows everything we have for it: the text, section,
 * verse, evidence level, license, the full passage the answer was grounded on, and links.
 * openId / onToggle are owned by MessageBubble so an inline [S1] marker can open its source.
 */
export function SourceCitation({ sources, scope, openId, onToggle }) {
  useEffect(() => {
    if (!openId) return;
    document.getElementById(sourceDomId(scope, openId))?.scrollIntoView?.({ behavior: "smooth", block: "nearest" });
  }, [openId, scope]);

  if (!sources?.length) return null;

  return (
    <div className="mt-3 border-t border-line/60 pt-2.5">
      <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-text-muted">
        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
        </svg>
        Sources ({sources.length}) <span className="font-normal text-text-faint">· tap one to read it</span>
      </p>
      <ul className="space-y-1.5">
        {sources.map((s, i) => {
          const id = s.id || `S${i + 1}`;
          const open = openId === id;
          return (
            <li
              key={id}
              id={sourceDomId(scope, id)}
              className={`overflow-hidden rounded-lg border transition-colors ${open ? "border-brand/40" : "border-line"}`}
            >
              <button
                type="button"
                onClick={() => onToggle(open ? null : id)}
                aria-expanded={open}
                className="flex w-full items-center gap-2 px-3 py-2 text-left text-xs hover:bg-brand-50/60"
              >
                <span className="shrink-0 rounded bg-brand-50 px-1.5 py-0.5 text-[10px] font-semibold text-brand-700">{id}</span>
                <span className="flex-1 truncate text-text">{sourceLabel(s)}</span>
                {s.url && <span className="shrink-0 text-[10px] text-text-faint">link</span>}
                <svg
                  className={`h-3 w-3 shrink-0 text-text-faint transition-transform duration-150 ${open ? "rotate-180" : ""}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                </svg>
              </button>
              {open && <SourceDetails source={s} />}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
