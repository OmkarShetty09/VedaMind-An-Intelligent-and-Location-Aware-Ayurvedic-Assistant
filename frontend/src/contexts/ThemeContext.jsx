import { createContext, useContext, useMemo, useState } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(() => localStorage.getItem("vedamind_theme") || "light");
  const value = useMemo(() => {
    const toggle = () =>
      setTheme((t) => {
        const next = t === "light" ? "dark" : "light";
        localStorage.setItem("vedamind_theme", next);
        return next;
      });
    return { theme, toggle };
  }, [theme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}
