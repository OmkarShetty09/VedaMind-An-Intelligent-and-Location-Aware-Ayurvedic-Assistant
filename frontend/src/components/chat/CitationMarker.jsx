import { useEffect, useRef, useState } from "react";

export function CitationMarker({ id, citation }) {
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
        title={`Source: ${citation.source}`}
      >
        {label}
      </span>
      {open && (
        <span
          ref={tooltipRef}
          style={{ position: "fixed", top: pos.top, left: pos.left, zIndex: 50 }}
          className="max-w-xs rounded-xl border border-line bg-white p-3 shadow-elevated animate-fade-in"
        >
          <p className="text-xs font-semibold text-text">{citation.source}</p>
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
        </span>
      )}
    </>
  );
}
