import { useState } from "react";
import { Outlet } from "react-router-dom";

import { ErrorBoundary } from "../common/ErrorBoundary.jsx";
import { Footer } from "./Footer.jsx";
import { Header } from "./Header.jsx";
import { Sidebar } from "./Sidebar.jsx";

export function AppShell() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen flex-col bg-surface-warm">
      <Header mobileMenuOpen={mobileMenuOpen} onToggleMenu={() => setMobileMenuOpen(!mobileMenuOpen)} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar mobileMenuOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)} />
        <main className="flex-1 overflow-y-auto">
          <div className="page-container">
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}
