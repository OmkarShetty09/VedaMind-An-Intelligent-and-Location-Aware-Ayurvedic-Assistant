import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";

import { authApi } from "../api/auth.js";
import { Button } from "../components/common/Button.jsx";
import { useAuthContext } from "../contexts/AuthContext.jsx";
import { setUser } from "../store/authSlice.js";

const toLines = (items, key) => (items || []).map((i) => i[key]).join("\n");
const fromLines = (text) =>
  text
    .split(/[\n,]/)
    .map((s) => s.trim())
    .filter(Boolean);

export function ProfilePage() {
  const { user } = useAuthContext();
  const dispatch = useDispatch();
  const [meds, setMeds] = useState("");
  const [conditions, setConditions] = useState("");
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState(null);

  useEffect(() => {
    setMeds(toLines(user?.medications, "free_text"));
    setConditions(toLines(user?.conditions, "condition"));
  }, [user?.medications, user?.conditions]);

  const save = async (e) => {
    e.preventDefault();
    setSaving(true);
    setNotice(null);
    try {
      await authApi.updateMedications(fromLines(meds));
      await authApi.updateConditions(fromLines(conditions));
      dispatch(setUser(await authApi.me()));
      setNotice({ type: "ok", text: "Saved. The safety check now uses these for every answer." });
    } catch (err) {
      setNotice({ type: "error", text: err.message });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="page-title">Profile</h1>
        <p className="page-subtitle">Your account information.</p>
      </div>
      <div className="card p-5 space-y-4">
        <div className="flex items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-xl font-bold text-brand">
            {user?.email?.charAt(0).toUpperCase() || "U"}
          </div>
          <div>
            <p className="text-base font-medium text-text">{user?.name || user?.email}</p>
            <p className="mt-0.5 text-sm text-text-muted">{user?.email}</p>
            <p className="mt-0.5 text-xs text-text-faint">
              Timezone: {user?.timezone || "UTC"} · {user?.consent_accepted ? "Consent accepted" : "Consent not accepted"}
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={save} className="card p-5 space-y-4">
        <div>
          <h2 className="section-title">Health details</h2>
          <p className="mt-1 text-sm text-text-muted">
            VedaMind checks every herb it discusses against these before answering. One item per line.
          </p>
        </div>
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-text">Current medications</span>
          <textarea
            value={meds}
            onChange={(e) => setMeds(e.target.value)}
            rows={3}
            placeholder={"e.g. warfarin 5 mg\nmetformin"}
            className="w-full rounded-xl border border-line bg-white px-3.5 py-2.5 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/10"
          />
        </label>
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-text">Conditions</span>
          <textarea
            value={conditions}
            onChange={(e) => setConditions(e.target.value)}
            rows={2}
            placeholder={"e.g. pregnancy\ntype 2 diabetes"}
            className="w-full rounded-xl border border-line bg-white px-3.5 py-2.5 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/10"
          />
        </label>
        {notice && (
          <div
            className={`rounded-lg border px-3 py-2 text-sm ${
              notice.type === "ok" ? "border-green-200 bg-green-50 text-green-800" : "border-red-200 bg-red-50 text-red-700"
            }`}
          >
            {notice.text}
          </div>
        )}
        <Button type="submit" loading={saving}>
          Save health details
        </Button>
      </form>
    </div>
  );
}
