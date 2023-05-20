from os import getenv

from minio import Minio


def get_minio() -> Minio:
    return Minio("minio:9000", getenv("MINIO_ROOT_USER"), getenv("MINIO_ROOT_PASSWORD"), secure=False)
