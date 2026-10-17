/**
 * Minimal Markdown for chat answers. The LLM writes headings, bullets and **bold**; showing the raw
 * symbols looks broken, while a full Markdown renderer would also have to understand [S#] markers.
 */

/** Line-level syntax -> plain text with **bold** markers (headings) and "•" bullets. */
export function normalizeMarkdown(text) {
  return (text || "")
    .split("\n")
    .map((line) => {
      if (/^\s*([-*_])\1{2,}\s*$/.test(line)) return "";
      const heading = line.match(/^\s*#{1,6}\s+(.*)$/);
      if (heading) return `**${heading[1].replace(/\*\*/g, "").trim()}**`;
      return line.replace(/^(\s*)[*-]\s+/, "$1• ");
    })
    .join("\n");
}

const INLINE_RE = /\*\*(.+?)\*\*|\*(?=\S)([^*\n]+?)\*/g;

/** **bold** and *italic* inside one text run; unmatched markers are dropped. */
export function renderInline(text, keyPrefix = "f") {
  const out = [];
  let last = 0;
  let match;
  let i = 0;
  INLINE_RE.lastIndex = 0;
  while ((match = INLINE_RE.exec(text)) !== null) {
    if (match.index > last) out.push(text.slice(last, match.index));
    if (match[1] !== undefined) out.push(<strong key={`${keyPrefix}-${i++}`}>{match[1]}</strong>);
    else out.push(<em key={`${keyPrefix}-${i++}`}>{match[2]}</em>);
    last = INLINE_RE.lastIndex;
  }
  if (last < text.length) out.push(text.slice(last));
  return out.map((part) => (typeof part === "string" ? part.replace(/\*\*/g, "") : part));
}
