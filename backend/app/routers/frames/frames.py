import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from routers.authorization.pydantic_models import GetMe, GetUser
from routers.authorization.service import get_user
from routers.frames.pydantic_models import CreateFrame, FrameOneResponse, FrameAllResponse, Pagination, \
    PagedResponseSchema
from routers.frames.responses import Responses
from routers.frames.service import Service

router = APIRouter()


@router.get(
    "/frames/",
    response_model=PagedResponseSchema[FrameAllResponse]
)
async def get_frames(
        pagination: Annotated[Pagination, Depends()],
        user: Annotated[GetMe, Depends(get_user)],
        service: Annotated[Service, Depends()],
        me: bool = False
):
    result = await service.get_frames(user, me, pagination)
    return PagedResponseSchema(
        total=len(result),
        results=result,
        **pagination.dict()
    )


@router.post(
    "/frames/",
    response_model=FrameOneResponse,
    status_code=HTTP_201_CREATED
)
async def create_frames(
        user: Annotated[GetUser, Depends(get_user)],
        service: Annotated[Service, Depends()],
        create_data: Annotated[CreateFrame, Depends(CreateFrame.to_form)],
        files: Annotated[List[UploadFile], File(...)] = None
):
    if not files or len(files) > 15:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.ZERO_OR_MANY_FILES)

    # if not await service.is_category_exists(create_data.category_id):
    #     raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.CATEGORY_DOES_NOT_EXISTS)

    return await service.create_frame(user, files, **create_data.dict())


@router.get(
    "/frames/{frame_uuid}/",
    response_model=FrameOneResponse
)
async def get_frame(
        user: Annotated[GetMe, Depends(get_user)],
        frame_uuid: uuid.UUID,
        service: Annotated[Service, Depends()]
):
    return await service.get_one_frame(user, frame_uuid)


@router.delete(
    "/frames/{frame_uuid}/",
    status_code=HTTP_204_NO_CONTENT,
    responses={204: {"model": None}}
)
async def delete_frame(
        frame_uuid: uuid.UUID,
        user: Annotated[GetMe, Depends(get_user)],
        service: Annotated[Service, Depends()]
):
    await service.delete_frame(frame_uuid, user)


@router.post(
    "/frames/{frame_uuid}/like/",
)
async def toggle_like_frame(
        frame_uuid: uuid.UUID,
        user: Annotated[GetMe, Depends(get_user)],
        service: Annotated[Service, Depends()]
):
    await service.toggle_like(frame_uuid, user.id)
    count = 0
    count_likes = await service.get_likes(frame_uuid)
    print(count_likes)
    if count_likes:
        count = count_likes[0][1]

    return {"count": count}
