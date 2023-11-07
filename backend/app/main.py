from fastapi import FastAPI, APIRouter
from pydantic import ValidationError

from dependencies.lifecycle import lifespan
from dependencies.exceptions import validation_exception_handler
from routers.authorization import authorization
from routers.categories import categories
from routers.frames import frames

app = FastAPI(
    title="VixenSpan",
    version="2.3.5",
    lifespan=lifespan,
    exception_handlers={ValidationError: validation_exception_handler}
)


router = APIRouter(prefix="/api/v1")
router.include_router(authorization.router)
router.include_router(authorization.users_router)
router.include_router(categories.router)
router.include_router(frames.router)
app.include_router(router)
