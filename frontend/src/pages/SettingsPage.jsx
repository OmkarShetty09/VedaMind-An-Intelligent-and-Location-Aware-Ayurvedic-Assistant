import { useAuthContext } from "../contexts/AuthContext.jsx";
import { useTheme } from "../contexts/ThemeContext.jsx";
import { Button } from "../components/common/Button.jsx";

export function SettingsPage() {
  const { user } = useAuthContext();
  const { theme, toggle } = useTheme();
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-text">Settings</h1>
      <div className="space-y-4">
        <div className="rounded-xl border border-line bg-surface p-4">
          <p className="text-sm font-medium text-text">Account</p>
          <p className="mt-1 text-sm text-text-muted">{user?.email}</p>
        </div>
        <div className="flex items-center justify-between rounded-xl border border-line bg-surface p-4">
          <div>
            <p className="text-sm font-medium text-text">Theme</p>
            <p className="mt-1 text-sm text-text-muted">{theme === "light" ? "Light" : "Dark"}</p>
          </div>
          <Button variant="secondary" onClick={toggle}>
            Toggle
          </Button>
        </div>
      </div>
    </div>
  );
}
