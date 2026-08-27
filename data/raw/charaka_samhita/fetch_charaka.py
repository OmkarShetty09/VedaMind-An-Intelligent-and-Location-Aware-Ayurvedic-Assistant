#!/usr/bin/env python3
"""Fetcher for Charaka Samhita from carakasamhitaonline.com (CC BY-NC-SA 4.0).

Downloads chapter content and normalizes into source.md format for VedaMind ingestion.

Usage:
    python fetch_charaka.py              # Fetch all chapters
    python fetch_charaka.py --chapter 1  # Fetch specific chapter
    python fetch_charaka.py --dry-run    # Show what would be fetched

Source: https://www.carakasamhitaonline.com/
License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
"""

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

try:
    import httpx
except ImportError:
    print("httpx not installed. Run: pip install httpx")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE_URL = "https://www.carakasamhitaonline.com/index.php"
OUTPUT_DIR = Path(__file__).resolve().parent  # same directory as this script

# Sutra Sthana chapters (30 chapters)
# Format: (chapter_number, page_title, english_name)
SUTRA_STHANA_CHAPTERS = [
    (1, "Deerghanjiviteeya_Adhyaya", "Longevity"),
    (2, "Apamarga_Tanduliya_Adhyaya", "Apamarga and Tanduliya"),
    (3, "Aragvadhiya_Adhyaya", "Aragvadhiya"),
    (4, "Shadvirechanashatashritiya_Adhyaya", "Sixfold Purgation"),
    (5, "Matrashiteeya_Adhyaya", "Matrashiteeya"),
    (6, "Tasyashiteeya_Adhyaya", "Tasyashiteeya"),
    (7, "Naveganadharaniya_Adhyaya", "Naveganadharaniya"),
    (8, "Indriyopakramaniya_Adhyaya", "Indriyopakramaniya"),
    (9, "Khuddakachatushpada_Adhyaya", "Khuddakachatushpada"),
    (10, "Mahachatushpada_Adhyaya", "Mahachatushpada"),
    (11, "Tistraishaniya_Adhyaya", "Tistraishaniya"),
    (12, "Vatakalakaliya_Adhyaya", "Vatakalakaliya"),
    (13, "Snehadhyaya", "Snehadhyaya"),
    (14, "Swedadhyaya", "Swedadhyaya"),
    (15, "Upakalpaniya_Adhyaya", "Upakalpaniya"),
    (16, "Chikitsaprabhritiya_Adhyaya", "Chikitsaprabhritiya"),
    (17, "Kiyanta_Shiraseeya_Adhyaya", "Kiyanta Shiraseeya"),
    (18, "Trishothiya_Adhyaya", "Trishothiya"),
    (19, "Ashtodariya_Adhyaya", "Ashtodariya"),
    (20, "Maharoga_Adhyaya", "Maharoga"),
    (21, "Ashtauninditiya_Adhyaya", "Ashtauninditiya"),
    (22, "Langhanabrimhaniya_Adhyaya", "Langhanabrimhaniya"),
    (23, "Santarpaniya_Adhyaya", "Santarpaniya"),
    (24, "Vidhishonitiya_Adhyaya", "Vidhishonitiya"),
    (25, "Yajjah_Purushiya_Adhyaya", "Yajjah Purushiya"),
    (26, "Atreyabhadrakapyiya_Adhyaya", "Atreyabhadrakapyiya"),
    (27, "Annapanavidhi_Adhyaya", "Annapanavidhi"),
    (28, "Vividhashitapitiya_Adhyaya", "Vividhashitapitiya"),
    (29, "Dashapranayataneeya_Adhyaya", "Dashapranayataneeya"),
    (30, "Arthedashmahamooliya_Adhyaya", "Arthedashmahamooliya"),
]

# Other sthanas (partial list for pilot)
OTHER_STHANAS = [
    ("Nidana_Sthana", "Nidana Sthana", "Diagnostic Principles"),
    ("Vimana_Sthana", "Vimana Sthana", "Specific Medical Principles"),
    ("Sharira_Sthana", "Sharira Sthana", "Human Being and Genesis"),
    ("Chikitsa_Sthana", "Chikitsa Sthana", "Therapeutic Principles"),
]


def fetch_page(title: str, client: httpx.Client) -> str | None:
    """Fetch raw wikitext content from the MediaWiki API."""
    params = {
        "action": "query",
        "titles": title,
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "formatversion": "2",
    }
    try:
        resp = client.get(BASE_URL, params=params, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get("query", {}).get("pages", [])
        if pages and pages[0].get("revisions"):
            return pages[0]["revisions"][0]["slots"]["main"]["content"]
    except Exception as e:
        logger.warning("Failed to fetch %s: %s", title, e)
    return None


def fetch_html(title: str, client: httpx.Client) -> str | None:
    """Fetch rendered HTML content from the wiki page."""
    params = {"title": title}
    try:
        resp = client.get(f"https://www.carakasamhitaonline.com/index.php", params=params, timeout=30.0)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning("Failed to fetch HTML for %s: %s", title, e)
    return None


def extract_text_from_html(html: str) -> str:
    """Extract readable text from HTML, preserving structure."""
    # Remove script and style tags
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    # Remove navigation, footer, etc.
    html = re.sub(r"<div[^>]*id=\"mw-(?:head|panel|footer|data\"[^>]*>.*?</div)", "", html, flags=re.DOTALL)
    # Convert headers
    html = re.sub(r"<h1[^>]*>(.*?)</h1>", r"\n# \1\n", html)
    html = re.sub(r"<h2[^>]*>(.*?)</h2>", r"\n## \1\n", html)
    html = re.sub(r"<h3[^>]*>(.*?)</h3>", r"\n### \1\n", html)
    html = re.sub(r"<h4[^>]*>(.*?)</h4>", r"\n#### \1\n", html)
    # Convert paragraphs
    html = re.sub(r"<p[^>]*>", "\n", html)
    html = re.sub(r"</p>", "\n", html)
    # Remove all other tags
    html = re.sub(r"<[^>]+>", "", html)
    # Decode HTML entities
    html = html.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    html = html.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    # Clean up whitespace
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html.strip()


def normalize_to_chapter(html: str, chapter_num: int, english_name: str) -> str:
    """Convert fetched content to source.md chapter format."""
    # The content is already in a readable format from the wiki
    # We need to extract the meaningful parts
    text = extract_text_from_html(html)

    # Find the main content section (after metadata, before navigation)
    # Look for the chapter content start
    lines = text.split("\n")
    content_lines = []
    in_content = False

    for line in lines:
        stripped = line.strip()
        # Skip metadata/navigation lines
        if any(skip in stripped.lower() for skip in [
            "jump to navigation", "jump to search", "from charak samhita",
            "navigation menu", "personal tools", " namespaces ", " views ",
            " search ", "playstore", "social-links", "donate", "in other languages",
            "content is available under", "privacy policy", "about charak samhita",
            "disclaimers", "mobile view", "page was last edited",
        ]):
            continue
        if stripped.startswith("http") or stripped.startswith("[!"):
            continue
        if stripped:
            in_content = True
        if in_content:
            content_lines.append(line)

    return "\n".join(content_lines)


def write_attribution_notice(output_dir: Path):
    """Write LICENSE Attribution file."""
    notice = """# Attribution Notice

## Source
Charak Samhita New Edition (Wiki)
https://www.carakasamhitaonline.com/

## License
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
https://creativecommons.org/licenses/by-nc-sa/4.0/

## Organization
Charak Samhita Research, Training and Skill Development Centre
National Institute of Indian Medical Heritage (NIIMH)
Central Council for Research in Ayurveda and Siddha (CCRAS)
Government of India

## Citation
Charak Samhita New Edition. Editors: Deole Y.S., Basisht G.
Available at: https://www.carakasamhitaonline.com/
DOI: https://doi.org/10.47468/CSNE.2020

## VedaMind Usage
This content is used for the VedaMind Ayurvedic wellness assistant under
the CC BY-NC-SA 4.0 license for non-commercial educational purposes.
"""
    (output_dir / "ATTRIBUTION.md").write_text(notice, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Fetch Charaka Samhita from carakasamhitaonline.com")
    parser.add_argument("--chapter", type=int, help="Fetch specific chapter number (1-30)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fetched")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    args = parser.parse_args()

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    chapters = SUTRA_STHANA_CHAPTERS
    if args.chapter:
        chapters = [(n, t, e) for n, t, e in chapters if n == args.chapter]
        if not chapters:
            logger.error("Chapter %d not found. Valid range: 1-30", args.chapter)
            sys.exit(1)

    if args.dry_run:
        logger.info("Would fetch %d chapters:", len(chapters))
        for num, title, name in chapters:
            logger.info("  Chapter %d: %s (%s)", num, title, name)
        return

    # Write attribution
    write_attribution_notice(output_dir)

    # Fetch chapters
    source_md_parts = []
    source_md_parts.append("# Sutra Sthana - Section on Fundamental Principles\n")
    source_md_parts.append("The Sutra Sthana is the first section of Charaka Samhita, dealing with fundamental principles of Ayurveda.\n")

    client = httpx.Client(
        headers={"User-Agent": "VedaMind/1.0 (Educational Research; CC BY-NC-SA 4.0)"},
        follow_redirects=True,
    )

    fetched = 0
    for num, title, name in chapters:
        logger.info("Fetching Chapter %d: %s...", num, title)
        html = fetch_html(title, client)
        if not html:
            logger.warning("Could not fetch Chapter %d (%s)", num, title)
            continue

        chapter_content = normalize_to_chapter(html, num, name)
        if chapter_content:
            source_md_parts.append(f"\n# Chapter {num}: {name}\n")
            source_md_parts.append(chapter_content)
            fetched += 1
            logger.info("  -> Chapter %d fetched (%d chars)", num, len(chapter_content))
        else:
            logger.warning("  -> Chapter %d: no content extracted", num)

        time.sleep(args.delay)

    client.close()

    # Write source.md
    source_md = "\n\n".join(source_md_parts)
    source_path = output_dir / "source.md"
    source_path.write_text(source_md, encoding="utf-8")
    logger.info("Wrote source.md: %d chars, %d chapters", len(source_md), fetched)

    logger.info("Done. %d chapters fetched.", fetched)
    logger.info("Next steps:")
    logger.info("  1. Review data/raw/charaka_samhita/source.md")
    logger.info("  2. Verify metadata.json and rights_manifest.json")
    logger.info("  3. Run: python -m app.ingestion validate")
    logger.info("  4. Run: python -m app.ingestion ingest --corpus charaka_samhita")


if __name__ == "__main__":
    main()
