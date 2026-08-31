export function Input({ label, error, className = "", ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-sm font-medium text-text">{label}</span>}
      <input
        className={`w-full rounded-xl border bg-white px-3.5 py-2.5 text-sm outline-none transition-all duration-150 focus:border-brand focus:ring-2 focus:ring-brand/10 ${
          error ? "border-red-400 focus:border-red-500 focus:ring-red-100" : "border-line"
        } ${className}`}
        {...props}
      />
      {error && <span className="mt-1.5 block text-xs text-red-600">{error}</span>}
    </label>
  );
}
