import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.routes import content, telegram

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Content Batching Engine API")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Content Batching Engine API")


app = FastAPI(
    title="Content Batching Engine",
    description="Backend system for transforming videos into omnichannel content using AI",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content.router)
app.include_router(telegram.router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "service": "content-batching-engine"}


@app.get("/")
async def root():
    return {
        "service": "Content Batching Engine",
        "version": "1.0.0",
        "docs": "/docs"
    }
