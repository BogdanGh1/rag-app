# RAG App

A full-stack application for building private, queryable knowledge bases from your documents. Upload PDFs or plain text, then ask questions and get answers grounded in your content, with source citations.

## How it works

Each user can create multiple named databases, each backed by a different retrieval strategy:

| Backend | Technology | Best for |
|---------|-----------|----------|
| `vector` | ChromaDB + OpenAI embeddings | Semantic / conceptual search |
| `sql` *(WIP)* | SQLite | Exact keyword matching  |
| `plaintext` | BM25 (`rank-bm25`) | Lightweight ranking without embeddings |

Documents are chunked on upload using configurable settings (chunk size, overlap, or section-based splitting), then indexed into the chosen backend. Queries run through a LangChain LCEL chain that retrieves relevant chunks and passes them to an OpenAI LLM to generate a grounded answer.

All data is fully isolated per user — storage paths embed both user ID and database ID.

## Stack

- **Backend:** FastAPI + LangChain + Python 3.13 (`uv`)
- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS + TanStack Query
- **Auth:** JWT + bcrypt (user records in PostgreSQL)
- **Config storage:** MongoDB (per-database chunking settings)
- **LLM / Embeddings:** OpenAI (`gpt-4o-mini` + `text-embedding-3-small` by default)

## Quickstart

**Prerequisites:** Docker, Python 3.13 + [`uv`](https://docs.astral.sh/uv/), Node.js 18+, OpenAI API key.

```bash
# 1. Start PostgreSQL + MongoDB
docker compose up -d

# 2. Set up backend
cd backend && uv sync --extra dev
cp .env.example .env   # set OPENAI_API_KEY and SECRET_KEY

# 3. Set up frontend
cd ../frontend && npm install

# 4. Start everything
cd .. && ./start.sh
```

- App: http://localhost:5173
- API docs: http://localhost:8000/docs

