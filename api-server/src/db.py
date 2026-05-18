import asyncio
from asyncpg import create_pool, Pool
from typing import Type, TypeVar

from main import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASS

conn_pool: Pool | None = None

async def init_db_conn():
    global conn_pool
    conn_pool = await create_pool(
        user=POSTGRES_USER,
        password=POSTGRES_PASS,
        database=POSTGRES_DB,
        host="localhost"
    )

async def close_db_conn():
    global conn_pool
    if conn_pool:
        await conn_pool.close()

T = TypeVar("T")

async def db_query_one(cls: Type[T], query: str, *args) -> T | None:
    async with conn_pool.acquire() as conn:
        result = await conn.fetchrow(query, *args)
        return cls(**result) if result is not None else None

async def db_query(cls: Type[T], query: str, *args) -> list[T]:
    async with conn_pool.acquire() as conn:
        return [cls(**dict(r)) for r in await conn.fetch(query, *args)]
    
async def db_execute(query: str, *args):
    async with conn_pool.acquire() as conn:
        await conn.execute(query, *args)