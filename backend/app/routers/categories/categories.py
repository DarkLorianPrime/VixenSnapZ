from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, File, UploadFile
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from routers.categories.responses import Responses
from routers.categories.service import Service

router = APIRouter(prefix="/categories")


@router.post("/create", status_code=HTTP_201_CREATED)
async def create_category(
        service: Annotated[Service, Depends()],
        name: str = Form(...),
        banner: UploadFile = File(...)
):
    if not banner:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=Responses.BANNER_IS_REQUIRED
        )

    is_category_exists = await service.is_category_exists(name)
    if is_category_exists:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=Responses.CATEGORY_EXISTS
        )

    return await service.create_category(name, banner)


@router.get("/")
async def get_categories():
    return []