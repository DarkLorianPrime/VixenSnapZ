from fastapi import Depends, UploadFile
from minio import Minio
from sqlalchemy import exists
from sqlalchemy.ext.asyncio import AsyncSession

from storages.database import get_session
from storages.s3 import get_minio
from routers.categories.models import Category


class Service:
    def __init__(self, session: AsyncSession = Depends(get_session), minio: Minio = Depends(get_minio)):
        self.session = session
        self.minio = minio

    async def save_banner(self, banner: UploadFile):
        self.minio.put_object(
            bucket_name="banners",
            object_name=banner.filename,
            data=banner.file,
            length=-1,
            part_size=10485760
        )

    async def create_category(self, category_name: str, banner: UploadFile):
        category = Category(
            name=category_name,
            banner=banner.filename
        )

        await self.save_banner(banner)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def is_category_exists(self, category_name):
        stmt = exists().where(Category.name == category_name).select()
        result = await self.session.execute(stmt)
        return result.scalar()
