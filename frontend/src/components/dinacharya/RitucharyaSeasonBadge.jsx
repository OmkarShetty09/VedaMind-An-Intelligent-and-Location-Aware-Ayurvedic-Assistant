export function RitucharyaSeasonBadge({ season }) {
  const ritu = {
    vasant: { label: "Vasant (Spring)", emoji: "🌸" },
    grishma: { label: "Grishma (Summer)", emoji: "☀️" },
    varsha: { label: "Varsha (Monsoon)", emoji: "🌧️" },
    sharad: { label: "Sharad (Autumn)", emoji: "🍂" },
    hemant: { label: "Hemant (Early Winter)", emoji: "🍁" },
    shishir: { label: "Shishir (Late Winter)", emoji: "❄️" },
  };
  if (!season) return null;
  const info = ritu[season] || { label: season, emoji: "🌿" };
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-brand/30 bg-brand-light px-3 py-1 text-xs font-medium text-brand">
      <span>{info.emoji}</span> {info.label}
    </div>
  );
}
