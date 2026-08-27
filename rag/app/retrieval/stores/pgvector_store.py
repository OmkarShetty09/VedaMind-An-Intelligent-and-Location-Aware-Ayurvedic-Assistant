"""Postgres + pgvector dense and tsvector sparse in one table we own."""

import logging
import hashlib

import psycopg
from psycopg.types.json import Jsonb

from .base import Passage, VectorStore

logger = logging.getLogger("rag.retrieval.pgvector")

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS rag_chunks (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding vector NOT NULL,
    fts tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    corpus_id TEXT,
    source_type TEXT,
    content_hash TEXT,
    chunk_index INTEGER,
    rights_status TEXT
);
"""


class PgVectorStore(VectorStore):
    """Postgres + pgvector dense and tsvector sparse in one table we own."""

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._ensure_table()

    def _connect(self):
        return psycopg.connect(self._dsn)

    def _ensure_table(self):
        with self._connect() as conn:
            conn.execute(_CREATE_TABLE)
            conn.execute("CREATE INDEX IF NOT EXISTS rag_chunks_fts ON rag_chunks USING GIN (fts);")
            conn.execute("CREATE INDEX IF NOT EXISTS rag_chunks_hnsw ON rag_chunks USING hnsw (embedding vector_cosine_ops);")
            conn.execute("CREATE INDEX IF NOT EXISTS rag_chunks_corpus ON rag_chunks (corpus_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS rag_chunks_source_type ON rag_chunks (source_type);")
            # Migrate existing tables: add columns if missing
            for col, typ in [
                ("corpus_id", "TEXT"),
                ("source_type", "TEXT"),
                ("content_hash", "TEXT"),
                ("chunk_index", "INTEGER"),
                ("rights_status", "TEXT"),
            ]:
                try:
                    conn.execute(f"ALTER TABLE rag_chunks ADD COLUMN {col} {typ}")
                except psycopg.errors.DuplicateColumn:
                    pass
            conn.commit()

    def search_dense(self, embedding, top_k, filters=None) -> list[Passage]:
        vec = "[" + ",".join(f"{v:.6f}" for v in embedding) + "]"
        where, params = _where_clause(filters)
        sql = f"""
            SELECT id, content, metadata, 1 - (embedding <=> %s::vector) AS score
            FROM rag_chunks {where}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        with self._connect() as conn:
            rows = conn.execute(sql, (vec, *params, vec, top_k)).fetchall()
        return [Passage(chunk_id=r[0], text=r[1], metadata=dict(r[2]), score=float(r[3])) for r in rows]

    def search_sparse(self, query, top_k, filters=None) -> list[Passage]:
        where, params = _where_clause(filters)
        cond = "fts @@ q"
        if where:
            cond += " AND " + where[len("WHERE "):]
        sql = f"""
            SELECT id, content, metadata, ts_rank(fts, q) AS score
            FROM rag_chunks, plainto_tsquery('english', %s) AS q
            WHERE {cond}
            ORDER BY score DESC
            LIMIT %s
        """
        with self._connect() as conn:
            rows = conn.execute(sql, (query, *params, top_k)).fetchall()
        return [Passage(chunk_id=r[0], text=r[1], metadata=dict(r[2]), score=float(r[3] or 0.0)) for r in rows]

    def upsert(self, chunks, embeddings) -> int:
        n = 0
        with self._connect() as conn:
            for chunk, emb in zip(chunks, embeddings):
                vec = "[" + ",".join(f"{v:.6f}" for v in emb) + "]"
                meta = chunk.get("metadata", {})
                content_hash = hashlib.sha256(chunk["content"].encode()).hexdigest()
                conn.execute(
                    """
                    INSERT INTO rag_chunks (id, content, metadata, embedding, corpus_id, source_type,
                                            content_hash, chunk_index, rights_status)
                    VALUES (%s, %s, %s, %s::vector, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE
                    SET content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding,
                        corpus_id = EXCLUDED.corpus_id,
                        source_type = EXCLUDED.source_type,
                        content_hash = EXCLUDED.content_hash,
                        chunk_index = EXCLUDED.chunk_index,
                        rights_status = EXCLUDED.rights_status
                    """,
                    (
                        chunk["id"],
                        chunk["content"],
                        Jsonb(meta),
                        vec,
                        meta.get("corpus_id"),
                        meta.get("source_type"),
                        content_hash,
                        meta.get("chunk_index"),
                        meta.get("rights_status"),
                    ),
                )
                n += 1
            conn.commit()
        logger.info("Upserted %s chunks", n)
        return n

    def count_chunks(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM rag_chunks").fetchone()
            return row[0] if row else 0

    def count_by_source(self) -> list[tuple[str, int]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT COALESCE(corpus_id, 'unknown'), COUNT(*) FROM rag_chunks GROUP BY corpus_id ORDER BY corpus_id"
            ).fetchall()
            return [(r[0], r[1]) for r in rows]

    def count_empty(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM rag_chunks WHERE content IS NULL OR TRIM(content) = ''").fetchone()
            return row[0] if row else 0

    def count_duplicate_hashes(self) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM (SELECT content_hash FROM rag_chunks WHERE content_hash IS NOT NULL "
                "GROUP BY content_hash HAVING COUNT(*) > 1) sub"
            ).fetchone()
            return row[0] if row else 0

    def source_types_in_use(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT DISTINCT source_type FROM rag_chunks WHERE source_type IS NOT NULL ORDER BY source_type"
            ).fetchall()
            return [r[0] for r in rows]


def _where_clause(filters: dict | None) -> tuple[str, list]:
    if not filters:
        return "", []
    conds = []
    params = []
    if filters.get("source"):
        conds.append("metadata->>'source' = %s")
        params.append(filters["source"])
    if filters.get("evidence_level"):
        conds.append("metadata->>'evidence_level' = %s")
        params.append(filters["evidence_level"])
    if filters.get("corpus_id"):
        conds.append("corpus_id = %s")
        params.append(filters["corpus_id"])
    if filters.get("source_type"):
        conds.append("source_type = %s")
        params.append(filters["source_type"])
    clause = "WHERE " + " AND ".join(conds) if conds else ""
    return clause, params
