import { EmptyState } from "../common/EmptyState.jsx";

export function RoutineEmptyState({ onRegenerate }) {
  return (
    <EmptyState
      icon="🌤️"
      title="No routine yet"
      description="Generate your personalized daily routine based on your local time, season, and weather."
      action={
        <button
          onClick={onRegenerate}
          className="mt-2 rounded-xl bg-brand px-5 py-2.5 text-sm font-medium text-white transition-all duration-150 hover:bg-brand-dark active:scale-[0.98]"
        >
          Generate routine
        </button>
      }
    />
  );
}
