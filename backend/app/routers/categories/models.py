from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from storages.database import Base


class Category(Base):
    __tablename__ = "category"

    banner: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
