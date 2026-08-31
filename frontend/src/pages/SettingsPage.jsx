import { useAuthContext } from "../contexts/AuthContext.jsx";
import { useTheme } from "../contexts/ThemeContext.jsx";

export function SettingsPage() {
  const { user } = useAuthContext();
  const { theme, toggle } = useTheme();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Manage your account and preferences.</p>
      </div>

      <section className="space-y-3">
        <h2 className="section-title">Profile</h2>
        <div className="card p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-text">Email</p>
              <p className="mt-0.5 text-sm text-text-muted">{user?.email}</p>
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
              </svg>
            </div>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="section-title">Preferences</h2>
        <div className="card p-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.752 9.752 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-text">Theme</p>
                <p className="mt-0.5 text-sm text-text-muted">{theme === "light" ? "Light" : "Dark"}</p>
              </div>
            </div>
            <button
              onClick={toggle}
              className="rounded-xl border border-line px-4 py-2 text-sm font-medium text-text-muted transition-all duration-150 hover:bg-brand-50 hover:text-text"
            >
              Toggle
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
