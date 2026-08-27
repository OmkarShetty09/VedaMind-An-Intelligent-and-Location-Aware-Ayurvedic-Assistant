const DOSHA_CONFIG = {
  vata: {
    label: "Vata",
    element: "Air & Space",
    color: "bg-teal-500",
    track: "bg-teal-100",
    textColor: "text-teal-700",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.75-11.25a.75.75 0 00-1.5 0v2.5h-2.5a.75.75 0 000 1.5h2.5v2.5a.75.75 0 001.5 0v-2.5h2.5a.75.75 0 000-1.5h-2.5v-2.5z" clipRule="evenodd" />
      </svg>
    ),
  },
  pitta: {
    label: "Pitta",
    element: "Fire & Water",
    color: "bg-amber-500",
    track: "bg-amber-100",
    textColor: "text-amber-700",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
        <path d="M10 2a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 2zm0 10a.75.75 0 01.75.75v1.5a.75.75 0 01-1.5 0v-1.5A.75.75 0 0110 12zm-6.25-2a.75.75 0 01.75-.75h1.5a.75.75 0 010 1.5h-1.5a.75.75 0 01-.75-.75zm10 0a.75.75 0 01.75-.75h1.5a.75.75 0 010 1.5h-1.5a.75.75 0 01-.75-.75z" />
        <path fillRule="evenodd" d="M10 6a4 4 0 100 8 4 4 0 000-8zm-2 4a2 2 0 114 0 2 2 0 01-4 0z" clipRule="evenodd" />
      </svg>
    ),
  },
  kapha: {
    label: "Kapha",
    element: "Earth & Water",
    color: "bg-emerald-600",
    track: "bg-emerald-100",
    textColor: "text-emerald-700",
    icon: (
      <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
        <path fillRule="evenodd" d="M4.606 12.97a.75.75 0 01-.134 1.057 4.973 4.973 0 00-.93-1.022c-.312-.292-.72-.454-1.147-.454-.427 0-.835.162-1.147.454a4.973 4.973 0 00-.93 1.022.75.75 0 01-1.191.903 6.473 6.473 0 011.238-1.336A6.47 6.47 0 0110 3.5a6.47 6.47 0 012.093.395 6.473 6.473 0 011.237 1.336.75.75 0 01-.925.966z" clipRule="evenodd" />
        <path fillRule="evenodd" d="M10 16.5a6.5 6.5 0 100-13 6.5 6.5 0 000 13zm0-1.5a5 5 0 110-10 5 5 0 010 10z" clipRule="evenodd" />
      </svg>
    ),
  },
};

export function DoshaScaleBar({ dosha, count, percentage, total, isPrimary, isSecondary }) {
  const pct = Math.max(0, Math.min(100, Math.round(percentage)));
  const cfg = DOSHA_CONFIG[dosha] || DOSHA_CONFIG.vata;

  return (
    <div className={`rounded-xl border p-3 transition-all ${
      isPrimary
        ? "border-brand bg-brand/5 shadow-sm"
        : isSecondary
        ? "border-line bg-surface/50"
        : "border-transparent bg-surface/30"
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className={cfg.textColor}>{cfg.icon}</span>
          <span className="text-sm font-medium text-text">{cfg.label}</span>
          <span className="text-xs text-text-muted">{cfg.element}</span>
          {isPrimary && (
            <span className="rounded-full bg-brand/10 px-2 py-0.5 text-xs font-medium text-brand">
              Primary
            </span>
          )}
          {isSecondary && (
            <span className="rounded-full bg-surface px-2 py-0.5 text-xs font-medium text-text-muted">
              Secondary
            </span>
          )}
        </div>
        <span className={`text-sm font-semibold ${cfg.textColor}`}>
          {count}/{total}
          <span className="ml-1 text-xs font-normal text-text-muted">({pct}%)</span>
        </span>
      </div>
      <div className={`mt-2 h-3 overflow-hidden rounded-full ${cfg.track}`}>
        <div
          className={`h-full rounded-full ${cfg.color} transition-all duration-700 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
