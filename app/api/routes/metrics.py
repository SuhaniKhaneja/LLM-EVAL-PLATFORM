from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.eval_schemas import MetricsOut
from app.services.eval_service import get_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("", response_model=MetricsOut)
async def metrics(db: AsyncSession = Depends(get_db)):
    return await get_metrics(db)