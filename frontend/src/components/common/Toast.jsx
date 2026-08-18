import { useToast } from "../../contexts/ToastContext.jsx";

const tone = {
  info: "border-brand/30 bg-white text-text",
  success: "border-green-300 bg-green-50 text-green-800",
  error: "border-red-300 bg-red-50 text-red-800",
  warning: "border-amber-300 bg-amber-50 text-amber-800",
};

export function Toast() {
  const { toasts, dismiss } = useToast();
  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-80 flex-col gap-2">
      {toasts.map((t) => (
        <button
          key={t.id}
          onClick={() => dismiss(t.id)}
          className={`pointer-events-auto flex items-start gap-2 rounded-xl border px-4 py-3 text-left text-sm shadow-lg ${tone[t.type] || tone.info}`}
        >
          <span className="flex-1">{t.message}</span>
          <span className="text-xs opacity-60">close</span>
        </button>
      ))}
    </div>
  );
}
