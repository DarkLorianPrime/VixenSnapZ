import uuid
from typing import List, Annotated

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from libraries.authenticator import verifier
from routers.authorization.pydantic_models import GetMe, GetUser
from routers.authorization.service import get_user
from routers.frames.pydantic_models import GetFrame, CreateFrame, FrameResponse, FrameOneResponse, FrameAllResponse
from routers.frames.responses import Responses
from routers.frames.service import Service

router = APIRouter()


@router.get(
    "/frames/",
    response_model=List[FrameAllResponse]
)
async def get_frames(user: verifier = Depends(verifier), service: Service = Depends(Service)):
    return await service.get_frames(user)


@router.post(
    "/frames/",
    response_model=FrameOneResponse,
    status_code=HTTP_201_CREATED
)
async def create_frames(
        user: Annotated[GetUser, Depends(get_user)],
        service: Annotated[Service, Depends()],
        create_data: Annotated[CreateFrame, Depends(CreateFrame.to_form)],
        files: List[UploadFile] = File(None)
):
    if not files or len(files) > 15:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.ZERO_OR_MANY_FILES)

    if not await service.is_category_exists(create_data.category_id):
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.CATEGORY_DOES_NOT_EXISTS)

    return await service.create_frame(user, files, **create_data.dict())


@router.get(
    "/frames/{frame_uuid}/",
    dependencies=[Depends(verifier)],
    response_model=FrameOneResponse
)
async def get_frame(frame_uuid: str, service: Service = Depends(Service)):
    return await service.get_one_frame(frame_uuid)


@router.delete(
    "/frames/{frame_uuid}/",
    status_code=HTTP_204_NO_CONTENT,
    responses={204: {"model": None}}
)
async def delete_frame(frame_uuid: str, service: Service = Depends(Service), user: verifier = Depends(verifier)):
    await service.delete_frame(frame_uuid, user)
