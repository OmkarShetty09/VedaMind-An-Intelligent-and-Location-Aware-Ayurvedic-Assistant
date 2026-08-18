import { useEffect, useState } from "react";

import { useAuthContext } from "../../contexts/AuthContext.jsx";
import { Button } from "../common/Button.jsx";

export function DisclaimerModal({ open, onAccept }) {
  const { acceptConsent } = useAuthContext();
  const [accepted, setAccepted] = useState(false);

  useEffect(() => {
    if (open) setAccepted(false);
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="text-lg font-semibold text-text">Please read before using VedaMind</h2>
        <div className="mt-3 space-y-2 text-sm leading-relaxed text-text-muted">
          <p>
            VedaMind provides educational wellness guidance based on classical Ayurvedic texts. It is <strong>not</strong>{" "}
            a medical device and does not provide diagnosis, treatment, or medical advice.
          </p>
          <p>
            Do not stop, start, or change any prescribed medication based on this app. If you are pregnant, nursing, or
            caring for a child, be especially careful: some herbs are not suitable.
          </p>
          <p>For any medical concern, please consult a qualified healthcare provider.</p>
        </div>
        <label className="mt-4 flex items-start gap-2 text-sm">
          <input type="checkbox" checked={accepted} onChange={(e) => setAccepted(e.target.checked)} className="mt-0.5" />
          I understand this is educational information only and not medical advice.
        </label>
        <div className="mt-5 flex justify-end gap-2">
          <Button
            disabled={!accepted}
            onClick={() => {
              acceptConsent();
              onAccept?.();
            }}
          >
            I agree
          </Button>
        </div>
      </div>
    </div>
  );
}
