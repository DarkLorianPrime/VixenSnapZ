from minio import Minio
import os
import dotenv


def connect_to_minio() -> Minio:
    dotenv.load_dotenv("libraries_deprecated/.env")
    return Minio(os.getenv("minio_url"), os.getenv("minio_login"), os.getenv("minio_password"), secure=False)
