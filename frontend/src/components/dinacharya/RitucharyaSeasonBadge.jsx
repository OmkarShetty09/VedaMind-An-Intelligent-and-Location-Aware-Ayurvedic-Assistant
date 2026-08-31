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
    <span className="inline-flex items-center gap-2 rounded-full border border-brand/20 bg-brand-50 px-3.5 py-1.5 text-xs font-medium text-brand-700">
      <span>{info.emoji}</span>
      {info.label}
    </span>
  );
}
