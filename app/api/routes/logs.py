from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.eval_schemas import PaginatedLogs
from app.services.eval_service import get_logs

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("", response_model=PaginatedLogs)
async def logs(page: int = Query(1, ge=1),
               page_size: int = Query(20, ge=1, le=100),
               db: AsyncSession = Depends(get_db)):
    return await get_logs(db, page, page_size)
