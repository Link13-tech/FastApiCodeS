from fastapi import Depends
from sqlalchemy.ext.asyncio import (async_sessionmaker, create_async_engine, AsyncSession, AsyncEngine, AsyncConnection)
from core.config import settings
from typing import Union, Callable, Annotated


class InternalError(Exception):
    pass


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except InternalError:
            await session.rollback()


def create_session_maker(
        bind_engine: Union[AsyncEngine, AsyncConnection]
) -> Callable[..., async_sessionmaker]:
    return async_sessionmaker(
        bind=bind_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


engine = create_async_engine(settings.postgres_dsn.unicode_string())

async_session = create_session_maker(engine)

db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
