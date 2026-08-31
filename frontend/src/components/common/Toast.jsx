import { useToast } from "../../contexts/ToastContext.jsx";

const tone = {
  info: "border-brand/20 bg-white text-text shadow-elevated",
  success: "border-green-200 bg-green-50 text-green-800 shadow-elevated",
  error: "border-red-200 bg-red-50 text-red-800 shadow-elevated",
  warning: "border-amber-200 bg-amber-50 text-amber-800 shadow-elevated",
};

export function Toast() {
  const { toasts, dismiss } = useToast();
  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-80 flex-col gap-2">
      {toasts.map((t) => (
        <button
          key={t.id}
          onClick={() => dismiss(t.id)}
          className={`pointer-events-auto flex items-start gap-3 rounded-xl border px-4 py-3 text-left text-sm animate-slide-up ${tone[t.type] || tone.info}`}
        >
          <span className="flex-1">{t.message}</span>
          <span className="text-xs text-text-faint">dismiss</span>
        </button>
      ))}
    </div>
  );
}
