from fastapi import APIRouter

from app.api import auth, backends, databases, documents, models, query

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(backends.router, prefix="/backends", tags=["backends"])
api_router.include_router(databases.router, prefix="/databases", tags=["databases"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(query.router, tags=["query"])
