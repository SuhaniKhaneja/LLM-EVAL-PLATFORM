import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.eval_models import Prompt, Response, EvalResult
from app.services.llm_service import call_llm
from app.evaluation.scorer import compute_scores
from app.schemas.eval_schemas import (
    EvaluateRequest, EvaluateResponse, ScoresOut,
    LogEntry, PaginatedLogs, MetricsOut
)

async def run_evaluation(req: EvaluateRequest, db: AsyncSession) -> EvaluateResponse:
    llm = await call_llm(req.prompt, req.max_tokens)
    scores = compute_scores(llm.text, req.reference)

    prompt_row = Prompt(text=req.prompt)
    db.add(prompt_row); await db.flush()

    resp_row = Response(
        prompt_id=prompt_row.id, text=llm.text, model=llm.model,
        latency_ms=llm.latency_ms,
        prompt_tokens=llm.prompt_tokens, completion_tokens=llm.completion_tokens,
    )
    db.add(resp_row); await db.flush()

    eval_row = EvalResult(
        response_id=resp_row.id,
        length_score=scores.length_score,
        rouge1_score=scores.rouge1_score,
        toxicity_score=scores.toxicity_score,
        is_toxic=scores.is_toxic,
        overall_score=scores.overall_score,
    )
    db.add(eval_row); await db.commit()

    return EvaluateResponse(
        prompt_id=prompt_row.id, response_id=resp_row.id,
        evaluation_id=eval_row.id,
        prompt=req.prompt, response=llm.text, model=llm.model,
        latency_ms=llm.latency_ms,
        prompt_tokens=llm.prompt_tokens, completion_tokens=llm.completion_tokens,
        scores=ScoresOut(**scores.__dict__),
        created_at=eval_row.created_at,
    )

async def get_logs(db: AsyncSession, page: int, page_size: int) -> PaginatedLogs:
    total = (await db.execute(select(func.count()).select_from(EvalResult))).scalar_one()
    stmt = (
        select(Prompt.id.label("prompt_id"), Prompt.text.label("prompt"),
               Response.id.label("response_id"), Response.text.label("response"),
               Response.model, Response.latency_ms,
               EvalResult.id.label("evaluation_id"),
               EvalResult.overall_score, EvalResult.is_toxic, EvalResult.created_at)
        .join(Response, Response.prompt_id == Prompt.id)
        .join(EvalResult, EvalResult.response_id == Response.id)
        .order_by(EvalResult.created_at.desc())
        .offset((page - 1) * page_size).limit(page_size)
    )
    rows = (await db.execute(stmt)).mappings().all()
    return PaginatedLogs(
        total=total, page=page, page_size=page_size,
        items=[LogEntry.model_validate(dict(r)) for r in rows]
    )

async def get_metrics(db: AsyncSession) -> MetricsOut:
    r = (await db.execute(
        select(func.count(EvalResult.id).label("total"),
               func.avg(EvalResult.overall_score).label("avg_score"),
               func.avg(Response.latency_ms).label("avg_latency"),
               func.avg(EvalResult.rouge1_score).label("avg_rouge1"))
        .join(Response, Response.id == EvalResult.response_id)
    )).mappings().one()
    toxic = (await db.execute(
        select(func.count()).where(EvalResult.is_toxic.is_(True))
    )).scalar_one()
    total = r["total"] or 0
    scores_q = (await db.execute(select(EvalResult.overall_score))).scalars().all()
    dist = {"poor":0,"fair":0,"good":0,"excellent":0}
    for s in scores_q:
        if s < 40: dist["poor"] += 1
        elif s < 60: dist["fair"] += 1
        elif s < 80: dist["good"] += 1
        else: dist["excellent"] += 1
    return MetricsOut(
        total_evaluations=total,
        avg_overall_score=round(float(r["avg_score"] or 0), 2),
        avg_latency_ms=round(float(r["avg_latency"] or 0), 2),
        toxic_count=toxic,
        toxic_rate=round(toxic / total, 4) if total else 0.0,
        avg_rouge1=round(float(r["avg_rouge1"] or 0), 4),
        score_distribution=dist,
    )