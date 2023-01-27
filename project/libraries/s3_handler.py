from os import getenv

from minio import Minio


def get_minio() -> Minio:
    return Minio("minio:9000", getenv("MINIO_USER"), getenv("MINIO_PASSWORD"), secure=False)
