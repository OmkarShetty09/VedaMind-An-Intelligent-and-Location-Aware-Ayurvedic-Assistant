import { EmptyState } from "../common/EmptyState.jsx";

export function RoutineEmptyState({ onRegenerate }) {
  return (
    <EmptyState
      icon="🌤️"
      title="No routine yet"
      description="Allow location access so we can tailor your routine to your local time and season."
      action={
        <button className="text-sm font-medium text-brand underline" onClick={onRegenerate}>
          Generate now
        </button>
      }
    />
  );
}
