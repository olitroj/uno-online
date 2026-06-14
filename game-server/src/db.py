import os
import asyncpg
from asyncpg import Pool

# Read the same DB env vars used by the API server
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_HOST = os.environ.get("DB_HOST")

conn_pool: Pool | None = None

async def init_db_conn():
    """Create the connection pool. Called once on server startup."""
    global conn_pool
    if DB_USER and DB_PASS and DB_NAME:
        conn_pool = await asyncpg.create_pool(
            user=DB_USER, password=DB_PASS, database=DB_NAME, host=DB_HOST
        )
        print("DB: connected")
    else:
        print("DB: no credentials set — game results will NOT be saved")

async def db_query_one(query: str, *args):
    if conn_pool is None:
        return None
    async with conn_pool.acquire() as conn:
        return await conn.fetchrow(query, *args)

async def db_execute(query: str, *args):
    if conn_pool is None:
        return
    async with conn_pool.acquire() as conn:
        return await conn.execute(query, *args)
