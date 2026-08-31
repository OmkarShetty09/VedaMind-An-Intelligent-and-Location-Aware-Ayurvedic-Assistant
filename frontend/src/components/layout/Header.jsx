import { Link } from "react-router-dom";

import { useAuthContext } from "../../contexts/AuthContext.jsx";

export function Header({ mobileMenuOpen, onToggleMenu }) {
  const { user, signOut } = useAuthContext();

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-line bg-surface/80 px-4 py-3 backdrop-blur-md lg:px-6">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleMenu}
          className="flex h-8 w-8 items-center justify-center rounded-lg text-text-muted transition-colors hover:bg-brand-light hover:text-text lg:hidden"
          aria-label="Toggle menu"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            {mobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            )}
          </svg>
        </button>
        <Link to="/" className="flex items-center gap-2.5 text-lg font-bold text-brand lg:hidden">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand text-sm text-white">🌿</span>
          VedaMind
        </Link>
      </div>
      <div className="flex items-center gap-3">
        {user && (
          <>
            <span className="hidden text-sm text-text-muted sm:block">{user.email}</span>
            <button
              onClick={signOut}
              className="rounded-lg px-3 py-1.5 text-sm font-medium text-text-muted transition-colors hover:bg-brand-light hover:text-text"
            >
              Sign out
            </button>
          </>
        )}
      </div>
    </header>
  );
}
