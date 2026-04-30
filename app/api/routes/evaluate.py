from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.eval_schemas import EvaluateRequest, EvaluateResponse
from app.services.eval_service import run_evaluation

router = APIRouter(prefix="/evaluate", tags=["evaluate"])

@router.post("", response_model=EvaluateResponse, status_code=201)
async def evaluate(req: EvaluateRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await run_evaluation(req, db)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))