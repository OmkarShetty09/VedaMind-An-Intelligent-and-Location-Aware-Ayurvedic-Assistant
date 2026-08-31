import { useAuthContext } from "../contexts/AuthContext.jsx";

export function ProfilePage() {
  const { user } = useAuthContext();
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
            <p className="text-base font-medium text-text">{user?.email}</p>
            <p className="mt-0.5 text-sm text-text-muted">
              {user?.consent_accepted ? "Consent accepted" : "Consent not accepted"}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
