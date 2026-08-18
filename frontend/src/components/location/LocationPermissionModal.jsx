import { Button } from "../common/Button.jsx";

export function LocationPermissionModal({ open, onRequest, onDismiss }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
        <h3 className="font-semibold text-text">Enable location?</h3>
        <p className="mt-2 text-sm text-text-muted">
          Your location lets us recommend the right daily routine and season for your local time and weather. It is
          never shared outside this app.
        </p>
        <div className="mt-5 flex justify-end gap-2">
          <Button variant="ghost" onClick={onDismiss}>
            Not now
          </Button>
          <Button onClick={onRequest}>Enable</Button>
        </div>
      </div>
    </div>
  );
}
