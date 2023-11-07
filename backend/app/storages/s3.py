from os import getenv

from minio import Minio


def get_minio() -> Minio:
    return Minio(
        endpoint="minio:9000",
        access_key=getenv("MINIO_ROOT_USER"),
        secret_key=getenv("MINIO_ROOT_PASSWORD"),
        secure=False
    )
