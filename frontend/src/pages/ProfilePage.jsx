import { useAuthContext } from "../contexts/AuthContext.jsx";

export function ProfilePage() {
  const { user } = useAuthContext();
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-text">Profile</h1>
      <div className="rounded-xl border border-line bg-surface p-4 text-sm">
        <p><span className="text-text-muted">Email:</span> {user?.email}</p>
        <p className="mt-1">
          <span className="text-text-muted">Consent:</span>{" "}
          {user?.consent_accepted ? "Accepted" : "Not accepted"}
        </p>
      </div>
    </div>
  );
}
