from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.base import init_db

from app.api.routes.evaluate import router as eval_router
from app.api.routes.logs import router as logs_router
from app.api.routes.metrics import router as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="LLM Evaluation Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ✅ FIXED HERE
for router in [eval_router, logs_router, metrics_router]:
    app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}