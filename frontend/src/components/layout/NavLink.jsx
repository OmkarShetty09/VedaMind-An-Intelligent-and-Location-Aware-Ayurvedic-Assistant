import { NavLink as RRNavLink } from "react-router-dom";

export function NavLink({ to, children, end = false, icon, onClick, className = "" }) {
  return (
    <RRNavLink
      to={to}
      end={end}
      onClick={onClick}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150 ${
          isActive
            ? "bg-brand text-white shadow-sm"
            : "text-text-muted hover:bg-brand-50 hover:text-text"
        } ${className}`
      }
    >
      {icon && <span className="flex h-5 w-5 shrink-0 items-center justify-center">{icon}</span>}
      {children}
    </RRNavLink>
  );
}
