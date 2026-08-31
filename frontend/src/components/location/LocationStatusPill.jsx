const state = {
  granted: { label: "Location on", cls: "bg-green-100 text-green-800 border-green-200" },
  denied: { label: "Location off", cls: "bg-amber-100 text-amber-800 border-amber-200" },
  prompt: { label: "Requesting...", cls: "bg-blue-100 text-blue-800 border-blue-200" },
  unsupported: { label: "Not supported", cls: "bg-gray-100 text-gray-600 border-gray-200" },
  unknown: { label: "No location", cls: "bg-gray-100 text-gray-600 border-gray-200" },
};

export function LocationStatusPill({ permission }) {
  const s = state[permission] || state.unknown;
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium ${s.cls}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {s.label}
    </span>
  );
}
