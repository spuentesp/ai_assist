from fastapi import APIRouter
from app.core.faiss_core import FaissCore

router = APIRouter()
faiss = FaissCore()

@router.get("/api/faiss")
async def faiss_json():
    return {"faiss": faiss.get_recent()}