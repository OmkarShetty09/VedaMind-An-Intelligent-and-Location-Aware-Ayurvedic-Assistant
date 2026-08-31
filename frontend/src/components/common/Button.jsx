export function Button({ variant = "primary", loading = false, className = "", children, ...props }) {
  const styles = {
    primary:
      "bg-brand text-white hover:bg-brand-dark shadow-sm hover:shadow-md active:scale-[0.98]",
    secondary:
      "border border-line bg-surface text-text hover:bg-brand-50 hover:border-brand-200 hover:text-brand-800 active:scale-[0.98]",
    ghost:
      "text-text-muted hover:bg-brand-50 hover:text-brand-800 active:scale-[0.98]",
    danger:
      "bg-danger text-white hover:opacity-90 active:scale-[0.98]",
  };

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium transition-all duration-150 disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}

export function Spinner({ size = "md", className = "" }) {
  const dim = { sm: "h-4 w-4", md: "h-5 w-5", lg: "h-8 w-8" }[size];
  return (
    <svg className={`animate-spin ${dim} ${className}`} viewBox="0 0 24 24" fill="none" aria-label="Loading">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}
