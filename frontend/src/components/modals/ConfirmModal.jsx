import { Button } from "../common/Button.jsx";

export function ConfirmModal({ open, title, message, onConfirm, onCancel, confirmLabel = "Confirm" }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
        <h3 className="font-semibold text-text">{title}</h3>
        {message && <p className="mt-2 text-sm text-text-muted">{message}</p>}
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={onCancel}>
            Cancel
          </Button>
          <Button variant="danger" onClick={onConfirm}>
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
