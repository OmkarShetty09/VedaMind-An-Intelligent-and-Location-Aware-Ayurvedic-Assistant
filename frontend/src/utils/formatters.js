export function formatTime(value) {
  if (!value) return "—";
  return value;
}

export function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString();
}

export function titleCase(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}
