import os
import sqlite3

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from rag_backends.base import StorageBackend

_INIT_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    filename    TEXT NOT NULL,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    content,
    document_id UNINDEXED,
    filename    UNINDEXED,
    chunk_index UNINDEXED
);
"""


class SQLRetriever(BaseRetriever):
    db_path: str
    top_k: int = 4

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        conn = sqlite3.connect(self.db_path)
        try:
            safe_query = query.replace('"', '""')
            cursor = conn.execute(
                """
                SELECT content, document_id, filename, chunk_index
                FROM   chunks_fts
                WHERE  chunks_fts MATCH ?
                ORDER  BY rank
                LIMIT  ?
                """,
                (safe_query, self.top_k),
            )
            rows = cursor.fetchall()
        except sqlite3.OperationalError:
            rows = []
        finally:
            conn.close()

        return [
            Document(
                page_content=row[0],
                metadata={
                    "document_id": row[1],
                    "filename": row[2],
                    "chunk_index": row[3],
                },
            )
            for row in rows
        ]


class SQLBackend(StorageBackend):
    name = "sql"

    def __init__(self, *, db_path: str):
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(_INIT_SQL)
            conn.commit()
        finally:
            conn.close()

    async def ingest(self, document_id: str, filename: str, chunks: list[Document]) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT OR REPLACE INTO documents (document_id, filename, chunk_count) VALUES (?, ?, ?)",
                (document_id, filename, len(chunks)),
            )
            for i, chunk in enumerate(chunks):
                conn.execute(
                    "INSERT INTO chunks_fts (content, document_id, filename, chunk_index) VALUES (?, ?, ?, ?)",
                    (chunk.page_content, document_id, filename, i),
                )
            conn.commit()
        finally:
            conn.close()
        return len(chunks)

    def get_retriever(self, top_k: int = 4) -> BaseRetriever:
        return SQLRetriever(db_path=self.db_path, top_k=top_k)

    async def list_documents(self) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "SELECT document_id, filename, chunk_count, created_at FROM documents"
            )
            rows = cursor.fetchall()
        finally:
            conn.close()
        return [
            {
                "document_id": row[0],
                "filename": row[1],
                "chunk_count": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]

    async def delete_document(self, document_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT document_id FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
            if not row:
                return False
            conn.execute("DELETE FROM chunks_fts WHERE document_id = ?", (document_id,))
            conn.execute("DELETE FROM documents WHERE document_id = ?", (document_id,))
            conn.commit()
        finally:
            conn.close()
        return True
