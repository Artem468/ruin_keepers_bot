from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base

from loader import engine

Base = declarative_base()


class Tour(Base):
    __tablename__ = "tours"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String)
    place = Column("place", String)
    price = Column("price", Float)
    max_members = Column("max_members", Integer)


class ScheduledTours(Base):
    __tablename__ = "scheduled_tours"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    tour_id = Column("tour_id", ForeignKey("tours.id", ondelete="CASCADE"))
    start_at = Column("start_at", DateTime)
    end_at = Column("end_at", DateTime)
    guide = Column("guide", String)


class Points(Base):
    __tablename__ = "points"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    tour_id = Column("tour_id", ForeignKey("tours.id", ondelete="CASCADE"))
    number = Column("number", Integer)
    name = Column("name", String)
    image = Column("image", String)


class Entries(Base):
    __tablename__ = "entries"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    scheduled_tour_id = Column("scheduled_tour_id", ForeignKey("scheduled_tours.id", ondelete="CASCADE"))
    telegram_id = Column("telegram_id", BigInteger)
    name = Column("name", String)
    email = Column("email", String)
    phone = Column("phone", String)
    is_need_lunch = Column("is_need_lunch", Boolean)
    is_need_notify = Column("is_need_notify", Boolean)
    count_members = Column("count_members", Integer)
    comment = Column("comment", String)


async def init_models() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
