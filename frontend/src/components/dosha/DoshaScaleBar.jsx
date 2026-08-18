const colors = { vata: "#b8860b", pitta: "#c2410c", kapha: "#2c5f2d" };

export function DoshaScaleBar({ dosha, score }) {
  const pct = Math.max(0, Math.min(100, Math.round((score / 3) * 100)));
  return (
    <div>
      <div className="flex justify-between text-xs text-text-muted">
        <span className="font-medium capitalize">{dosha}</span>
        <span>{score}</span>
      </div>
      <div className="mt-1 h-2 overflow-hidden rounded-full bg-brand-light">
        <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, background: colors[dosha] }} />
      </div>
    </div>
  );
}
