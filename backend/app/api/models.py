from fastapi import APIRouter

router = APIRouter()

_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4-turbo",
    "gpt-3.5-turbo",
]


@router.get("")
async def get_models() -> list[str]:
    return _MODELS
