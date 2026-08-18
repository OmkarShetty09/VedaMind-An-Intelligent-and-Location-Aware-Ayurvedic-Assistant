import { Navigate, Route, Routes } from "react-router-dom";

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
  if (loading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
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
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
