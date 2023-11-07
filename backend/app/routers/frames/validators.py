import re

from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from routers.frames.responses import Responses


async def filetype_validate(value: str) -> None | bool:
    if not re.search(r"\.(png|jpg|gif|jpeg|bmp|webp|svg)", value, re.IGNORECASE):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.NOT_IMAGE_TYPE)

    return True
