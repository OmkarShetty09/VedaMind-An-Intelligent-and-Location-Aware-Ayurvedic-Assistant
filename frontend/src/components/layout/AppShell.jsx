import { Outlet } from "react-router-dom";
import { ErrorBoundary } from "../common/ErrorBoundary.jsx";
import { Footer } from "./Footer.jsx";
import { Header } from "./Header.jsx";
import { Sidebar } from "./Sidebar.jsx";

export function AppShell() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="mx-auto w-full max-w-4xl flex-1 px-4 py-6">
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </main>
      </div>
      <Footer />
    </div>
  );
}
