from fastapi import APIRouter, HTTPException

from app.utils.database import DB

router = APIRouter(prefix="/status", tags=["Status"])


@router.get("/health")
def health() -> dict[str, str]:
    """
    Check if server is running\n
    ---
    **return:** {"status": "ok"}
    """
    return {"status": "ok"}


@router.get("/readiness")
async def readiness() -> dict[str, str]:
    """
    Check if server properly communicate with database\n
    ---
    **return:** {"status": "ok"}
    """

    if await DB.check_connection():
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=503, detail="Connection to database failed")
