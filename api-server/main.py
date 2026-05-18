import os

JWT_SECRET = "9bxhAgLv4W5PhW4VNglCj4KQjEmLnLZy"
SESSION_LENGTH = 2*3600

POSTGRES_USER = os.environ.get("DB_USER")
POSTGRES_PASS = os.environ.get("DB_PASS")
POSTGRES_DB =  os.environ.get("DB_NAME")

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.db import init_db_conn, close_db_conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_conn()
    yield
    await close_db_conn()

app = FastAPI(lifespan=lifespan)

import src.endpoints as endpoints