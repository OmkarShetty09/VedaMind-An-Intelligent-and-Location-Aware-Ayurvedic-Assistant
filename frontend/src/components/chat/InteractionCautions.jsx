const SEVERITY_STYLES = {
  severe: "bg-red-100 text-red-700",
  high: "bg-red-100 text-red-700",
  moderate: "bg-amber-100 text-amber-800",
  low: "bg-gray-100 text-gray-700",
};

const KIND_LABELS = { medicine: "Modern medicine", herb: "Herb", condition: "Condition" };

function capitalize(text) {
  return text ? text[0].toUpperCase() + text.slice(1) : "";
}

/**
 * "What not to take it with", shown under every answer. cautions: {herbs, items, general, note} from
 * the backend's curated interaction rules (apps/guardrails/cautions.py).
 */
export function InteractionCautions({ cautions }) {
  if (!cautions?.general) return null;
  const items = cautions.items || [];

  return (
    <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50/70 px-3 py-2.5 text-xs text-text">
      <p className="flex items-center gap-1.5 font-semibold text-amber-800">
        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
        </svg>
        What not to take it with
      </p>
      {items.length > 0 && (
        <ul className="mt-2 space-y-2">
          {items.map((item, i) => (
            <li
              key={i}
              className={`rounded-lg border bg-white/70 px-2.5 py-2 ${item.applies_to_you ? "border-red-300" : "border-amber-200/70"}`}
            >
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="font-semibold">{capitalize(item.herb)}</span>
                <span className="text-text-faint">+</span>
                <span className="font-semibold">{item.avoid_with}</span>
                <span className="text-[10px] text-text-faint">{KIND_LABELS[item.kind] || item.kind}</span>
                {item.severity && (
                  <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium capitalize ${SEVERITY_STYLES[item.severity] || SEVERITY_STYLES.low}`}>
                    {item.severity} risk
                  </span>
                )}
                {item.applies_to_you && (
                  <span className="rounded bg-red-600 px-1.5 py-0.5 text-[10px] font-medium text-white">You take this</span>
                )}
              </div>
              {item.examples?.length > 0 && (
                <p className="mt-0.5 text-[11px] text-text-muted">Includes e.g. {item.examples.join(", ")}</p>
              )}
              <p className="mt-1 leading-relaxed">{item.recommendation}</p>
              {(item.evidence || item.source_uri) && (
                <p className="mt-1 text-[11px] text-text-faint">
                  {item.evidence && <span className="capitalize">Evidence: {item.evidence}</span>}
                  {item.evidence && item.source_uri && " · "}
                  {item.source_uri && (
                    <a
                      href={item.source_uri}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-brand underline-offset-2 hover:underline"
                    >
                      Source ↗
                    </a>
                  )}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
      {cautions.note && <p className="mt-2 leading-relaxed text-text-muted">{cautions.note}</p>}
      <p className="mt-2 leading-relaxed text-text-muted">{cautions.general}</p>
    </div>
  );
}
