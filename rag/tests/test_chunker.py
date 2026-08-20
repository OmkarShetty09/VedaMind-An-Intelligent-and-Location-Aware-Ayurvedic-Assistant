"""Never split a shloka; prose keeps full coverage via overlap."""

from app.ingestion.chunker import chunk_document

VERSE_DOC = {
    "id": "cs:adhyaya-1",
    "source": "charaka_samhita",
    "chapter": "Sutrasthana 1",
    "content": (
        "1. Line of first shloka with quite a lot of words to fill space here.\n"
        "2. Second shloka continues the thought and adds more detail.\n"
        "3. Third shloka closes the section.\n"
        "\n"
        "This is prose commentary about the above verses. It goes on for a while "
        "explaining things in normal sentences without numbers."
    ),
    "evidence_level": "classical",
}


def test_verse_lines_are_never_split():
    chunks = chunk_document(VERSE_DOC, chunk_size=1000, overlap=100)
    for c in chunks:
        if c["metadata"]["verse"]:
            for line in c["content"].splitlines():
                if line.strip():
                    assert line[0].isdigit() or line.strip()[0] in "0123456789", f"verse line split: {line!r}"


def test_prose_coverage_is_complete():
    chunks = chunk_document(VERSE_DOC, chunk_size=6, overlap=2)
    prose = " ".join(c["content"] for c in chunks if not c["metadata"]["verse"])
    prose_words = set(VERSE_DOC["content"].split("\n\n", 1)[1].split())
    for w in prose_words:
        assert w in prose, f"lost word: {w}"


def test_no_verse_duplicated_across_chunks():
    chunks = chunk_document(VERSE_DOC, chunk_size=100, overlap=100)
    verse_lines = [line for c in chunks if c["metadata"]["verse"] for line in c["content"].splitlines() if line.strip()]
    assert len(verse_lines) == 3, f"expected 3 verse lines, got {len(verse_lines)}"