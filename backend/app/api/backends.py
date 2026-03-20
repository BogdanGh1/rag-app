from fastapi import APIRouter, HTTPException

from app.core.retriever_factory import list_backends, set_active_backend
from app.models.requests import SetActiveBackendRequest
from app.models.responses import BackendInfo, BackendsResponse

router = APIRouter()


@router.get("", response_model=BackendsResponse)
async def get_backends():
    backends = list_backends()
    active = next(b["name"] for b in backends if b["active"])
    return BackendsResponse(
        backends=[BackendInfo(**b) for b in backends],
        active=active,
    )


@router.put("/active")
async def set_backend(request: SetActiveBackendRequest):
    try:
        set_active_backend(request.backend)
        return {"active": request.backend}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))
