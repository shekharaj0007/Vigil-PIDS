from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.database import init_db
from app.routers.api import router
from app.services.http_client import close_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield
    await close_client()


app = FastAPI(
    title="Vigil PIDS — Weather Sensor Calibration",
    description=(
        "Smart module that analyzes live weather and recommends "
        "perimeter sensor sensitivity to reduce false intrusion alarms."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(router)
