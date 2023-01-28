import datetime
import uuid
from typing import List

import pytz
from fastapi import Depends, UploadFile, HTTPException
from minio import Minio
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST

from libraries.database import get_session
from libraries.s3_handler import get_minio
from routers.frames.models import InBox
from routers.frames.responses import Responses


class Service:
    def __init__(self, session: AsyncSession = Depends(get_session), minio: Minio = Depends(get_minio)):
        self.session = session
        self.minio = minio

    async def is_frame_exists(self, user_id: int, file_uuid: uuid.UUID):
        query = exists().where(InBox.user_id == user_id, InBox.file_uuid == file_uuid).select()
        is_user_exists = await self.session.execute(query)
        return is_user_exists.scalar()

    async def get_frame(self, user_id: int | None = None, file_uuid: str | None = None):
        query = []
        if user_id is not None:
            query.append(InBox.user_id == user_id)

        if file_uuid is not None:
            query.append(InBox.file_uuid == file_uuid)

        query = await self.session.execute(select(InBox).where(*query))
        return query.scalars().first()

    async def get_frames(self, user: dict):
        bucket_name = datetime.datetime.now().strftime("%Y%m%d")
        response = []
        if not self.minio.bucket_exists(bucket_name):
            self.minio.make_bucket(bucket_name)

        for frame in self.minio.list_objects(bucket_name):
            file_uuid = frame.object_name.replace(".png", "")
            file = await self.get_frame(user_id=user["id"], file_uuid=file_uuid)

            if not file:
                continue

            object_response = {"uuid": frame.object_name,
                               "uploaded": frame.last_modified.replace(tzinfo=pytz.timezone("Europe/Samara")).strftime(
                                   "%d.%m.%Y %H:%M:%S"),
                               "filename": file.filename}
            response.append(object_response)

        return response

    async def create_frame(self, user: dict, files: List[UploadFile]):
        bucket_name = datetime.datetime.now().strftime("%Y%m%d")

        if not self.minio.bucket_exists(bucket_name):
            self.minio.make_bucket(bucket_name)

        created = []
        for file in files:
            if ".png" not in file.filename and ".jpg" not in file.filename:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.NOT_IMAGE_TYPE)

            file_uuid = uuid.uuid4()
            created.append({
                "server_name": str(file_uuid),
                "filename": file.filename
            })

            box = InBox(filename=file.filename, file_uuid=file_uuid, bucketname=bucket_name, user_id=user["id"])
            self.session.add(box)
            await self.session.commit()

            self.minio.put_object(bucket_name=bucket_name,
                                  object_name=f"{file_uuid}.png",
                                  data=file.file,
                                  length=-1,
                                  part_size=10485760)

        return created

    async def get_one_frame(self, frame_uuid: str):
        frame = await self.get_frame(file_uuid=frame_uuid)

        if not frame:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.NOT_EXISTS_FRAME)

        bucket_name = datetime.datetime.now().strftime("%Y%m%d")
        item = [i for i in self.minio.list_objects(bucket_name=bucket_name) if frame_uuid in i.object_name]
        time = item[0].last_modified.replace(tzinfo=pytz.timezone("Europe/Samara"))

        return {
            "uploaded": time.strftime("%d.%m.%Y %H:%M:%S"),
            "uuid": frame_uuid,
            "filename": frame.filename
        }

    async def delete_frame(self, frame_uuid: str, user: dict):
        frame = await self.get_frame(user_id=user["id"], file_uuid=frame_uuid)

        if not frame:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=Responses.NOT_YOUR_FRAME)

        bucket_name = datetime.datetime.now().strftime("%Y%m%d")
        self.minio.remove_object(bucket_name, frame_uuid + ".png")

        await self.session.delete(frame)
        await self.session.commit()
