/** info: {key, label, emoji} from the backend's ritu calendar (backend/apps/dinacharya/data/ritu.json). */
export function RitucharyaSeasonBadge({ info }) {
  if (!info?.label) return null;
  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-brand/20 bg-brand-50 px-3.5 py-1.5 text-xs font-medium text-brand-700">
      {info.emoji && <span>{info.emoji}</span>}
      {info.label}
    </span>
  );
}
