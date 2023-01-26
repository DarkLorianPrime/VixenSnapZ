from fastapi import Depends
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession

from libraries.database import get_session
from libraries.s3_handler import get_minio


class Service:
    def __init__(self, session: AsyncSession = Depends(get_session), minio: Minio = Depends(get_minio)
                 ):
        self.session = session
        self.minio = minio
