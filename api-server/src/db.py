from asyncpg import create_pool, Pool, Record

from main import POSTGRES_DB, POSTGRES_USER, POSTGRES_PASS, POSTGRES_HOST

conn_pool: Pool | None = None

async def init_db_conn():
    global conn_pool
    conn_pool = await create_pool(
        user=POSTGRES_USER,
        password=POSTGRES_PASS,
        database=POSTGRES_DB,
        host=POSTGRES_HOST
    )

async def close_db_conn():
    global conn_pool
    if conn_pool:
        await conn_pool.close()

async def db_query_one(query: str, *args) -> Record | None:
    async with conn_pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def db_query(query: str, *args) -> list[Record]:
    async with conn_pool.acquire() as conn:
        return await conn.fetch(query, *args)
    
async def db_execute(query: str, *args) -> str:
    async with conn_pool.acquire() as conn:
        return await conn.execute(query, *args)