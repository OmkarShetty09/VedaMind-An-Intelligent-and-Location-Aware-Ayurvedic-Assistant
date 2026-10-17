import { Navigate, Route, Routes, useLocation } from "react-router-dom";

import { AppShell } from "./components/layout/AppShell.jsx";
import { useAuthContext } from "./contexts/AuthContext.jsx";
import { ChatPage } from "./pages/ChatPage.jsx";
import { DinacharyaPage } from "./pages/DinacharyaPage.jsx";
import { DoshaAssessmentPage } from "./pages/DoshaAssessmentPage.jsx";
import { HomePage } from "./pages/HomePage.jsx";
import { LoginPage } from "./pages/LoginPage.jsx";
import { NotFoundPage } from "./pages/NotFoundPage.jsx";
import { ProfilePage } from "./pages/ProfilePage.jsx";
import { RegisterPage } from "./pages/RegisterPage.jsx";
import { SettingsPage } from "./pages/SettingsPage.jsx";

function Protected({ children }) {
  const { isAuthenticated, loading } = useAuthContext();
  const location = useLocation();
  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return children;
}

/**
 * Login/register redirect once signed in: right after submitting, or on a refresh with a live session.
 * Goes back to the page that sent the user here, else /chat (which routes new users to onboarding).
 * Never gates on `loading`, so the form stays mounted (and keeps its error) while a sign-in is in flight.
 */
function GuestOnly({ children }) {
  const { isAuthenticated } = useAuthContext();
  const location = useLocation();
  if (isAuthenticated) return <Navigate to={location.state?.from || "/chat"} replace />;
  return children;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/chat" element={<Protected><ChatPage /></Protected>} />
        <Route path="/dinacharya" element={<Protected><DinacharyaPage /></Protected>} />
        <Route path="/dosha" element={<Protected><DoshaAssessmentPage /></Protected>} />
        <Route path="/profile" element={<Protected><ProfilePage /></Protected>} />
        <Route path="/settings" element={<Protected><SettingsPage /></Protected>} />
      </Route>
      <Route path="/login" element={<GuestOnly><LoginPage /></GuestOnly>} />
      <Route path="/register" element={<GuestOnly><RegisterPage /></GuestOnly>} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
