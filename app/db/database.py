# from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Теперь переменные доступны через os.getenv
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL не определен или пустой")

SQLALCHEMY_DATABASE_URL = database_url

engine = create_async_engine(
    database_url, echo=True, future=True
)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Настраиваем соединение с Redis
# redis_client = redis.Redis(host='redis', port=6380, db=0)

async def get_db():
    async with SessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass