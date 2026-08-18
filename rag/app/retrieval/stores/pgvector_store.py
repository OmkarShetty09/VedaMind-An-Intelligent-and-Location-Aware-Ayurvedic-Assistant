import logging

import psycopg
from psycopg.types.json import Jsonb

from .base import Passage, VectorStore

logger = logging.getLogger("rag.retrieval.pgvector")


class PgVectorStore(VectorStore):
    """Postgres + pgvector dense and tsvector sparse in one table we own."""

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._ensure_table()

    def _connect(self):
        return psycopg.connect(self._dsn)

    def _ensure_table(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rag_chunks (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                    embedding vector NOT NULL,
                    fts tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS rag_chunks_fts ON rag_chunks USING GIN (fts);")
            conn.execute("CREATE INDEX IF NOT EXISTS rag_chunks_hnsw ON rag_chunks USING hnsw (embedding vector_cosine_ops);")
            conn.commit()

    def search_dense(self, embedding, top_k, filters=None) -> list[Passage]:
        vec = "[" + ",".join(f"{v:.6f}" for v in embedding) + "]"
        where = _where_clause(filters)
        sql = f"""
            SELECT id, content, metadata, 1 - (embedding <=> %s::vector) AS score
            FROM rag_chunks {where}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        with self._connect() as conn:
            rows = conn.execute(sql, (vec, vec, top_k)).fetchall()
        return [Passage(chunk_id=r[0], text=r[1], metadata=dict(r[2]), score=float(r[3])) for r in rows]

    def search_sparse(self, query, top_k, filters=None) -> list[Passage]:
        where = _where_clause(filters)  # "" or "WHERE <cond>"
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
            rows = conn.execute(sql, (query, top_k)).fetchall()
        return [Passage(chunk_id=r[0], text=r[1], metadata=dict(r[2]), score=float(r[3] or 0.0)) for r in rows]

    def upsert(self, chunks, embeddings) -> int:
        n = 0
        with self._connect() as conn:
            for chunk, emb in zip(chunks, embeddings):
                vec = "[" + ",".join(f"{v:.6f}" for v in emb) + "]"
                conn.execute(
                    """
                    INSERT INTO rag_chunks (id, content, metadata, embedding)
                    VALUES (%s, %s, %s, %s::vector)
                    ON CONFLICT (id) DO UPDATE
                    SET content = EXCLUDED.content,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding
                    """,
                    (chunk["id"], chunk["content"], Jsonb(chunk["metadata"]), vec),
                )
                n += 1
            conn.commit()
        logger.info("Upserted %s chunks", n)
        return n


def _where_clause(filters: dict | None) -> str:
    if not filters:
        return ""
    conds = []
    if filters.get("source"):
        conds.append(f"metadata->>'source' = '{filters['source']}'")
    if filters.get("evidence_level"):
        conds.append(f"metadata->>'evidence_level' = '{filters['evidence_level']}'")
    return "WHERE " + " AND ".join(conds) if conds else ""


def get_pgvector_store() -> PgVectorStore:
    from app.deps_store import _pgvector_store

    return _pgvector_store()