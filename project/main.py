from fastapi import FastAPI, APIRouter

from libraries.database import engine, base
from routers.authorization import authorization
from routers.frames import frames


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)


app = FastAPI(title="DarkFileServer", version="2.3.5", on_startup=[create_database])
router = APIRouter(prefix="/api/v1")
router.include_router(authorization.router)
router.include_router(frames.router)
app.include_router(router)
