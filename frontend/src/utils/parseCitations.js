// Matches [S1] and grouped forms the model also writes: [S1, S5] / [S1, 5] / [S1; S2], also with the
// full-width brackets some models use (【S1】, ［S1］).
const CITATION_RE = /[[【［](S\d+(?:\s*[,;、]\s*S?\d+)*)[\]】］]/g;

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
    for (const part of match[1].split(/[,;、]/)) {
      const id = `S${part.trim().replace(/^S/, "")}`;
      segments.push({ type: "citation", id, raw: `[${id}]` });
    }
    lastIndex = CITATION_RE.lastIndex;
  }

  if (lastIndex < text.length) {
    segments.push({ type: "text", value: text.slice(lastIndex) });
  }

  return segments.length > 0 ? segments : [{ type: "text", value: text }];
}
