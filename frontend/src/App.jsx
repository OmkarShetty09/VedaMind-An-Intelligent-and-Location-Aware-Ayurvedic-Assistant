import { BrowserRouter } from "react-router-dom";

import { AuthProvider } from "./contexts/AuthContext.jsx";
import { LocationProvider } from "./contexts/LocationContext.jsx";
import { ThemeProvider } from "./contexts/ThemeContext.jsx";
import { AppRoutes } from "./routes.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <LocationProvider>
            <AppRoutes />
          </LocationProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
