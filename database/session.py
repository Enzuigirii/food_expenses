from __future__ import annotations

from typing import AsyncGenerator
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from settings import DATABASE_URL


class SessionContextManager:
    def __init__(self):
        self.engine = create_async_engine(
            DATABASE_URL,
            future=True,
            echo=True,
            execution_options={'isolation_level': 'AUTOCOMMIT'},
        )
        self.async_session: AsyncSession = async_sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def __aenter__(self):
        return self.async_session()

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.async_session().close()


async def get_async_session() -> Optional[AsyncGenerator]:
    async with SessionContextManager() as session:
        yield session
