# Adding Ayurvedic Data to VedaMind

Step-by-step guide for adding new Ayurvedic PDFs to the RAG knowledge base.

> **You do NOT manually chunk, embed, or index.** The pipeline handles all of that automatically. Your job is to convert the PDF to Markdown and place it in the right folder.

---

## Prerequisites

```bash
pip install pymupdf4llm
```

---

## Workflow

### Step 1: Convert PDF to Markdown

```python
import pymupdf4llm
import pathlib

pdf_path = pathlib.Path("path/to/your_book.pdf")
md_text = pymupdf4llm.to_markdown(str(pdf_path))
pdf_path.with_suffix(".md").write_text(md_text, encoding="utf-8")
```

Or via CLI:

```bash
python -c "import pymupdf4llm; print(pymupdf4llm.to_markdown('path/to/book.pdf'))" > book.md
```

**Review the output:**
- Ensure headings are preserved as `# Title` format
- The chunker splits on `# ` headings — each heading becomes a chapter
- Add or adjust `# ` lines manually if the PDF has no clear structure

---

### Step 2: Create Source Directory

```bash
mkdir data/raw/<your_source_id>
```

Use lowercase with underscores (e.g., `ashtanga_hridaya`, `bhavaprakasha`).

---

### Step 3: Place `source.md`

Move your converted file into the source directory and rename it:

```bash
mv book.md data/raw/<your_source_id>/source.md
```

---

### Step 4: Create `metadata.json`

**Minimum required** (1 field):

```json
{"corpus_id": "your_source_id"}
```

**Full template:**

```json
{
  "corpus_id": "your_source_id",
  "title": "Human-Readable Book Title",
  "source_type": "GENERAL",
  "language": "en",
  "author": "Author Name",
  "description": "Brief description of what this book covers",
  "sections": ["topic1", "topic2"]
}
```

**`source_type` taxonomy:**

| Type | Use For |
|---|---|
| `CLASSICAL` | Ancient texts (Charaka, Sushruta, Ashtanga Hridaya) |
| `DRAVYAGUNA` | Herb pharmacopeia, Nighantus |
| `MODERN_CLINICAL` | RCTs, meta-analyses, clinical studies |
| `GENERAL` | General Ayurvedic reference, textbooks |

---

### Step 5: Create `rights_manifest.json`

**Minimum required** (3 fields):

```json
{
  "verification_status": "VERIFIED",
  "rights_status": "PUBLIC_DOMAIN",
  "license": "Public Domain"
}
```

**For copyrighted works you have permission to use:**

```json
{
  "verification_status": "VERIFIED",
  "rights_status": "LICENSED",
  "license": "Used with permission"
}
```

> **Note:** `verification_status` MUST be `"VERIFIED"` or the source is skipped during ingestion.

---

### Step 6: Validate

```bash
cd rag
python -m app.ingestion status
python -m app.ingestion validate
```

Your new source should show status `READY` with `OK` for rights and metadata.

---

### Step 7: Ingest

Ingest all sources:

```bash
python -m app.ingestion ingest
```

Or ingest only your new source:

```bash
python -m app.ingestion ingest --corpus your_source_id
```

**What happens automatically:**
1. `source.md` is split into chapters (on `# ` headings)
2. Chapters are chunked (500 words, 100 word overlap, verse-aware)
3. Chunks are embedded (Gemini or OpenAI)
4. Embedded chunks are upserted into `rag_chunks` table in PostgreSQL

---

### Step 8: Verify

```bash
python -m app.ingestion report
```

Check that:
- Your `corpus_id` appears in the manifest
- Total chunk count increased
- Per-source breakdown shows your new source

Test retrieval:

```bash
curl -X POST http://localhost:8001/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "a topic from your new book"}'
```

Verify citations reference your new source.

---

## File Structure After Adding a Source

```
data/raw/
  your_source_id/
    source.md              ← your converted PDF
    metadata.json          ← corpus metadata (corpus_id required)
    rights_manifest.json   ← license info (3 fields required)
```

---

## What's Automatic (No Manual Work Needed)

| Step | Module | What It Does |
|---|---|---|
| Load | `rag/app/ingestion/loader.py` | Reads `source.md`, splits on `# ` headings |
| Verify | `rag/app/ingestion/verifier.py` | Checks `rights_manifest.json` + `metadata.json` |
| Chunk | `rag/app/ingestion/chunker.py` | 500-word windows, verse-aware, 100-word overlap |
| Embed | `rag/app/ingestion/embeddings.py` | Gemini or OpenAI, 1024 dimensions |
| Index | `rag/app/ingestion/indexer.py` | Upsert to pgvector, HNSW + GIN indexes |
| Manifest | `rag/app/ingestion/manifest.py` | Writes `chunks.jsonl` + `index_manifest.json` |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Source shows `NOT_AVAILABLE` | Ensure `source.md` exists and is not empty |
| Source shows `RIGHTS_UNVERIFIED` | Ensure `rights_manifest.json` has `verification_status: "VERIFIED"` |
| Source shows `FAILED` | Ensure `metadata.json` has `corpus_id` field |
| Ruff CI fails | Run `ruff check .` locally before pushing |
| `makemigrations --check` fails | Generate any missing migrations with `python manage.py makemigrations` |
