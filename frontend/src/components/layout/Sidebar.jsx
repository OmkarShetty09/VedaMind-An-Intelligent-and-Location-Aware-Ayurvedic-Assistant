import { NavLink } from "./NavLink.jsx";

const items = [
  { to: "/", label: "Home", end: true },
  { to: "/chat", label: "Chat" },
  { to: "/dinacharya", label: "Dinacharya" },
  { to: "/dosha", label: "Dosha Assessment" },
  { to: "/settings", label: "Settings" },
];

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col gap-1 border-r border-line bg-surface p-4 lg:flex">
      <div className="mb-4 flex items-center gap-2 px-1">
        <span className="text-lg">🌿</span>
        <span className="font-semibold text-brand">VedaMind</span>
      </div>
      {items.map((item) => (
        <NavLink key={item.to} to={item.to} end={item.end}>
          {item.label}
        </NavLink>
      ))}
    </aside>
  );
}
