# Stage 1: build the React/Vite frontend
FROM node:20-slim AS frontend
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: backend (FastAPI) + serve the built frontend
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app
COPY backend/ ./backend/
COPY --from=frontend /fe/dist ./frontend/dist
WORKDIR /app/backend
RUN uv sync --frozen --no-dev
ENV FRONTEND_DIST=/app/frontend/dist
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
