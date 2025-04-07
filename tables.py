from sqlalchemy import Column, BigInteger
from sqlalchemy.orm import declarative_base

from loader import engine

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"

    id = Column("id", BigInteger, primary_key=True)



async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
