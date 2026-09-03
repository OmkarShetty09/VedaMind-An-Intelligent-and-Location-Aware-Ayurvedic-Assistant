const CITATION_RE = /\[S(\d+)\]/g;

export function parseCitations(text) {
  if (!text) return [{ type: "text", value: "" }];

  const segments = [];
  let lastIndex = 0;
  let match;

  CITATION_RE.lastIndex = 0;
  while ((match = CITATION_RE.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({ type: "text", value: text.slice(lastIndex, match.index) });
    }
    segments.push({ type: "citation", id: `S${match[1]}`, raw: match[0] });
    lastIndex = CITATION_RE.lastIndex;
  }

  if (lastIndex < text.length) {
    segments.push({ type: "text", value: text.slice(lastIndex) });
  }

  return segments.length > 0 ? segments : [{ type: "text", value: text }];
}
