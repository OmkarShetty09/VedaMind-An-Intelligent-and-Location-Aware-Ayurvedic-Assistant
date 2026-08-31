"""Extract Charaka Samhita epub into a structured source.md for RAG ingestion.

Handles low-quality OCR by:
1. Stripping OCR accuracy notices and page markers
2. Removing garbled Devanagari fragments
3. Keeping readable Sanskrit verses and English translations
4. Splitting into chapter-level sections
"""
import re
import zipfile
from html.parser import HTMLParser
from pathlib import Path


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._text = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self._skip = False
        if tag in ("p", "br", "div", "h1", "h2", "h3", "h4", "li", "tr"):
            self._text.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._text.append(data)

    def get_text(self):
        return "".join(self._text)


def extract_page(z, name):
    html = z.read(name).decode("utf-8", errors="replace")
    te = TextExtractor()
    te.feed(html)
    return te.get_text().strip()


def clean_ocr_text(text):
    """Remove OCR artifacts and garbled text, keep readable content."""
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        s = line.strip()
        # Skip empty lines
        if not s:
            cleaned.append("")
            continue
        # Skip OCR accuracy notices
        if "estimated to be only" in s and "accurate" in s:
            continue
        # Skip page markers
        if re.match(r"^Page \d+$", s):
            continue
        # Skip lines that are mostly garbled (many consecutive non-ASCII chars without spaces)
        # Count ratio of readable chars
        ascii_chars = sum(1 for c in s if c.isascii() and c.isalpha())
        total_alpha = sum(1 for c in s if c.isalpha())
        if total_alpha > 0 and ascii_chars / total_alpha > 0.3:
            # Has enough readable content
            cleaned.append(s)
        elif total_alpha == 0:
            # No alphabetic chars (numbers, punctuation only)
            cleaned.append(s)
        else:
            # Mostly garbled Devanagari - try to extract verse numbers and structure
            # Keep lines with verse numbers (॥ १२३ ॥ pattern)
            if re.search(r"॥\s*\d+\s*॥", s) or re.search(r"१|२|३|४|५|६|७|८|९|०", s):
                # Has Devanagari numerals - might be a verse
                cleaned.append(s)
            # Keep lines with known English words
            elif any(w in s.lower() for w in ["chapter", "section", "fever", "treatment", "herb", "medicine", "dosha", "vata", "pitta", "kapha"]):
                cleaned.append(s)
    return "\n".join(cleaned)


def split_into_chapters(text):
    """Split cleaned text into chapter-level sections."""
    lines = text.split("\n")
    chapters = []
    current_title = "General Content"
    current_lines = []

    # Common chapter heading patterns in Charaka Samhita
    chapter_patterns = [
        r"(?i)^sutra\s+sthana",
        r"(?i)^nidana\s+sthana",
        r"(?i)^vimana\s+sthana",
        r"(?i)^sharira\s+sthana",
        r"(?i)^indriya\s+sthana",
        r"(?i)^chikitsa\s+sthana",
        r"(?i)^kalpa\s+sthana",
        r"(?i)^siddhi\s+sthana",
        r"(?i)^chapter\s+\d+",
        r"(?i)^adhyaya\s+\d+",
        r"(?i)^section\s+\d+",
    ]

    for line in lines:
        s = line.strip()
        is_heading = False
        for pat in chapter_patterns:
            if re.search(pat, s) and len(s) < 150:
                is_heading = True
                break

        if is_heading and len(s) > 3:
            if current_lines:
                chapters.append((current_title, "\n".join(current_lines)))
            current_title = s
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        chapters.append((current_title, "\n".join(current_lines)))

    return chapters


def main():
    epub_path = Path(r"C:\Users\OMKAR\Downloads\Charaka Samhita Text with English Tanslation - P.V. Sharma.epub")
    out_path = Path(r"C:\Users\OMKAR\OneDrive\Desktop\major project\VedaMind-An-Intelligent-and-Location-Aware-Ayurvedic-Assistant\data\raw\charaka_samhita\source.md")

    z = zipfile.ZipFile(epub_path)
    pages = sorted([n for n in z.namelist() if n.startswith("EPUB/page_") and n.endswith(".html")])

    print(f"Total pages: {len(pages)}")

    # Extract and clean all text
    all_text = []
    for i, page in enumerate(pages):
        txt = extract_page(z, page)
        cleaned = clean_ocr_text(txt)
        if cleaned.strip():
            all_text.append(cleaned)
        if i % 100 == 0:
            print(f"  processed {i}/{len(pages)}")

    full_text = "\n\n".join(all_text)
    print(f"\nCleaned text: {len(full_text)} chars")

    # Split into chapters
    chapters = split_into_chapters(full_text)
    print(f"Found {len(chapters)} chapters/sections")

    # Write source.md with # headings for each chapter
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("# Charaka Samhita - P.V. Sharma Translation\n\n")
        f.write("The Charaka Samhita is the foundational text of Ayurveda, written by Agnivesha and redacted by Charaka. ")
        f.write("It covers the fundamental principles of Ayurvedic medicine, diagnosis, treatment, and pharmaceutical preparations.\n\n")

        for title, content in chapters:
            # Clean up the title
            clean_title = re.sub(r"\s+", " ", title).strip()
            if len(clean_title) > 150:
                clean_title = clean_title[:150] + "..."

            f.write(f"# {clean_title}\n\n")
            # Write content, limiting to reasonable chunk size
            content_lines = content.strip().split("\n")
            # Remove excessive blank lines
            prev_blank = False
            for line in content_lines:
                if not line.strip():
                    if not prev_blank:
                        f.write("\n")
                    prev_blank = True
                else:
                    f.write(line + "\n")
                    prev_blank = False
            f.write("\n\n")

    file_size = out_path.stat().st_size
    print(f"\nWritten to {out_path} ({file_size} bytes, {file_size/1024:.1f} KB)")

    # Also write the full cleaned text for reference
    full_path = out_path.parent / "full_text" / "cleaned_text.txt"
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(full_text, encoding="utf-8")
    print(f"Full cleaned text: {full_path} ({len(full_text)} chars)")


if __name__ == "__main__":
    main()
