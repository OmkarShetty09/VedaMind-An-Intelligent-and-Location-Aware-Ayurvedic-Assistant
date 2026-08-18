import { NavLink as RRNavLink } from "react-router-dom";

export function NavLink({ to, children, end = false, className = "" }) {
  return (
    <RRNavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
          isActive ? "bg-brand text-white" : "text-text-muted hover:bg-brand-light/50 hover:text-text"
        } ${className}`
      }
    >
      {children}
    </RRNavLink>
  );
}
