from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from starlette.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from libraries.authenticator import verifier
from routers.frames.pydantic_models import GetFrame, CreateFrame
from routers.frames.responses import Responses
from routers.frames.service import Service

router = APIRouter()


@router.get("/frames/", response_model=List[GetFrame])
async def get_frames(user: verifier = Depends(verifier), service: Service = Depends(Service)):
    frames = await service.get_frames(user.__dict__)
    return frames


@router.post("/frames/", response_model=List[CreateFrame], status_code=HTTP_201_CREATED)
async def create_frames(user: verifier = Depends(verifier),
                        service: Service = Depends(Service),
                        files: List[UploadFile] = File(None)):
    if not files or len(files) > 15:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.ZERO_OR_MANY_FILES)

    return await service.create_frame(user.__dict__, files)


@router.get("/frames/{frame_uuid}/", dependencies=[Depends(verifier)], response_model=GetFrame)
async def get_frame(frame_uuid: str,
                    service: Service = Depends(Service),):

    return await service.get_one_frame(frame_uuid)


@router.delete("/frames/{frame_uuid}/", status_code=HTTP_204_NO_CONTENT, responses={204: {"model": None}})
async def delete_frame(frame_uuid: str, service: Service = Depends(Service), user: verifier = Depends(verifier)):
    await service.delete_frame(frame_uuid, user.__dict__)
    return
