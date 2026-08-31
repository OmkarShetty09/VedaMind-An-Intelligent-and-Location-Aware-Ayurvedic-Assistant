export function EmptyState({ icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center gap-4 rounded-2xl border border-dashed border-line bg-surface/50 px-6 py-12 text-center">
      {icon && <div className="text-4xl opacity-80">{icon}</div>}
      <div>
        <p className="text-base font-medium text-text">{title}</p>
        {description && <p className="mt-1.5 text-sm leading-relaxed text-text-muted">{description}</p>}
      </div>
      {action}
    </div>
  );
}
