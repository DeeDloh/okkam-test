import datetime as dt

from sqlalchemy import Date, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=False
    )
    date: Mapped[dt.date] = mapped_column(Date)
    respondent: Mapped[int] = mapped_column(Integer)
    sex: Mapped[int] = mapped_column(Integer)
    age: Mapped[int] = mapped_column(Integer)
    weight: Mapped[float] = mapped_column(Float(53))


class RespondentStats(Base):
    __tablename__ = "respondent_stats"

    respondent: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    sex: Mapped[int] = mapped_column(Integer)
    age: Mapped[int] = mapped_column(Integer)
    avg_weight: Mapped[float] = mapped_column(Float(53))