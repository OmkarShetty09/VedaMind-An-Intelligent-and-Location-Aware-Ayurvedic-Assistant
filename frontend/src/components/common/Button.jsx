export function Button({ variant = "primary", loading = false, className = "", children, ...props }) {
  const styles = {
    primary: "bg-brand text-white hover:bg-brand-dark disabled:bg-brand/50",
    secondary: "border border-line bg-surface hover:bg-brand-light/50 text-text",
    ghost: "text-brand hover:bg-brand-light/50",
    danger: "bg-[--danger] text-white hover:opacity-90",
  };
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors disabled:cursor-not-allowed ${styles[variant]} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  );
}

export function Spinner({ size = "md", className = "" }) {
  const dim = { sm: "h-4 w-4", md: "h-6 w-6", lg: "h-10 w-10" }[size];
  return (
    <svg className={`animate-spin text-brand ${dim} ${className}`} viewBox="0 0 24 24" fill="none" aria-label="Loading">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
    </svg>
  );
}
