from fastapi import APIRouter, Depends

from routers.frames.service import Service

router = APIRouter()


@router.get("/frames/")
async def get_frames(service: Service = Depends(Service)):
    print(service)