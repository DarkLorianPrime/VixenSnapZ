import json
from contextlib import asynccontextmanager

from storages.database import engine, Base
from storages.s3 import get_minio


@asynccontextmanager
async def lifespan(_):
    await create_database()
    await create_minio_buckets()
    yield


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_minio_buckets():
    minio = get_minio()
    access_json = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": [
                        "*"
                    ]
                },
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::*"
                ]
            }
        ]
    }
    for bucket_name in ["avatars", "banners", "frames"]:
        if not minio.bucket_exists(bucket_name):
            minio.make_bucket(bucket_name)

            minio.set_bucket_policy(bucket_name, json.dumps(access_json))
