"""NR1 AI — API backend (usada pelo app desktop via HTTP local, ou testável direto)."""
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI

from app.core.database.db import init_pool, close_pool
from app.modules.nr1.router import router as nr1_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield
    await close_pool()


app = FastAPI(title="NR1 AI", version="0.1.0-mvp", lifespan=lifespan)
app.include_router(nr1_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "nr1-ai"}
