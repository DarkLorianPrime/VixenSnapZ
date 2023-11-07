from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


async def validation_exception_handler(_: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "Error": "Name field is missing"}),
    )
