from fastapi import APIRouter

from app.core.retriever_factory import list_backend_names

router = APIRouter()


@router.get("")
async def get_backends() -> list[str]:
    return list_backend_names()
