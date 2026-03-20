from fastapi import APIRouter

from app.api import backends, documents, query

api_router = APIRouter()
api_router.include_router(backends.router, prefix="/backends", tags=["backends"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(query.router, tags=["query"])
