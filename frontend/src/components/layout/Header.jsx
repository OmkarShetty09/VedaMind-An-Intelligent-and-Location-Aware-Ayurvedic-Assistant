import { Link } from "react-router-dom";

import { useAuthContext } from "../../contexts/AuthContext.jsx";
import { Button } from "../common/Button.jsx";

export function Header() {
  const { user, signOut } = useAuthContext();
  return (
    <header className="flex items-center justify-between border-b border-line bg-surface px-4 py-3">
      <Link to="/" className="flex items-center gap-2 text-lg font-semibold text-brand lg:hidden">
        <span>🌿</span> VedaMind
      </Link>
      <div className="hidden lg:block" />
      <div className="flex items-center gap-3">
        {user && (
          <>
            <span className="text-sm text-text-muted">{user.email}</span>
            <Button variant="ghost" onClick={signOut}>
              Sign out
            </Button>
          </>
        )}
      </div>
    </header>
  );
}
