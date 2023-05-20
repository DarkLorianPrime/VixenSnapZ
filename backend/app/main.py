from fastapi import FastAPI, APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from libraries.database import engine, base
from routers.authorization import authorization
from routers.frames import frames


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)


app = FastAPI(title="DarkFileServer", version="2.3.5", on_startup=[create_database])


@app.exception_handler(ValidationError)
async def validation_exception_handler(_: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "Error": "Name field is missing"}),
    )

router = APIRouter(prefix="/api/v1")
router.include_router(authorization.router)
router.include_router(frames.router)
app.include_router(router)
