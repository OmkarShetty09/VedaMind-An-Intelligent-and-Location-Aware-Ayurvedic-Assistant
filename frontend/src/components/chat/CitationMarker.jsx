import { useEffect, useRef, useState } from "react";

/** onOpenSource(id): open this source in the message's source list (full passage + links). */
export function CitationMarker({ id, citation, onOpenSource }) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef(null);
  const tooltipRef = useRef(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (!open) return;

    const updatePosition = () => {
      if (triggerRef.current) {
        const rect = triggerRef.current.getBoundingClientRect();
        setPos({ top: rect.bottom + 6, left: rect.left });
      }
    };

    updatePosition();

    const handleMouseDown = (e) => {
      if (
        tooltipRef.current && !tooltipRef.current.contains(e.target) &&
        triggerRef.current && !triggerRef.current.contains(e.target)
      ) {
        setOpen(false);
      }
    };

    const handleEscape = (e) => {
      if (e.key === "Escape") setOpen(false);
    };

    document.addEventListener("mousedown", handleMouseDown);
    document.addEventListener("keydown", handleEscape);
    window.addEventListener("scroll", updatePosition, true);

    return () => {
      document.removeEventListener("mousedown", handleMouseDown);
      document.removeEventListener("keydown", handleEscape);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [open]);

  if (!citation) {
    return <span className="text-brand-600 font-medium">{id}</span>;
  }

  const label = `[${id}]`;

  return (
    <>
      <span
        ref={triggerRef}
        role="button"
        tabIndex={0}
        onClick={() => setOpen((prev) => !prev)}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); setOpen((prev) => !prev); } }}
        className="inline-flex items-center rounded bg-brand-50 px-1 text-[11px] font-semibold text-brand-700 cursor-pointer transition-colors hover:bg-brand-100 select-none align-baseline"
        title={`Source: ${citation.title || citation.source}`}
      >
        {label}
      </span>
      {open && (
        <span
          ref={tooltipRef}
          style={{ position: "fixed", top: pos.top, left: pos.left, zIndex: 50 }}
          className="block w-72 max-w-[calc(100vw-2rem)] rounded-xl border border-line bg-white p-3 shadow-elevated animate-fade-in"
        >
          <p className="text-xs font-semibold text-text">{citation.title || citation.source}</p>
          {(citation.chapter || citation.verse) && (
            <p className="mt-0.5 text-[11px] text-text-muted">
              {citation.chapter}{citation.verse ? ` : ${citation.verse}` : ""}
            </p>
          )}
          {citation.evidence_level && (
            <span className="mt-1.5 inline-block rounded bg-brand-50 px-1.5 py-0.5 text-[10px] font-medium text-brand-600">
              {citation.evidence_level}
            </span>
          )}
          {citation.excerpt && (
            <span className="mt-2 block max-h-28 overflow-hidden whitespace-pre-wrap text-[11px] leading-relaxed text-text-muted">
              {citation.excerpt.length > 280 ? `${citation.excerpt.slice(0, 280)}…` : citation.excerpt}
            </span>
          )}
          <span className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[11px]">
            {onOpenSource && (
              <button
                type="button"
                onClick={() => {
                  setOpen(false);
                  onOpenSource(id);
                }}
                className="font-medium text-brand underline-offset-2 hover:underline"
              >
                Read full passage
              </button>
            )}
            {citation.url && (
              <a
                href={citation.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-brand underline-offset-2 hover:underline"
              >
                Open source ↗
              </a>
            )}
          </span>
        </span>
      )}
    </>
  );
}
