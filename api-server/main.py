import os
import json
from fastapi import FastAPI
from contextlib import asynccontextmanager

POSTGRES_USER   = os.environ.get("DB_USER")
POSTGRES_PASS   = os.environ.get("DB_PASS")
POSTGRES_DB     = os.environ.get("DB_NAME")

from src.db import init_db_conn, close_db_conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    if POSTGRES_DB is not None and POSTGRES_USER is not None and POSTGRES_PASS is not None:
        await init_db_conn()
        yield
        await close_db_conn()
    else:
        yield

SPEC_PATH = os.environ.get("SPEC_PATH")

app = FastAPI(
    lifespan=lifespan,
    openapi_url="/openapi.json" if SPEC_PATH else None,
    docs_url="/docs" if SPEC_PATH else None,
    redoc_url="/redoc" if SPEC_PATH else None,
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    with open("../docs/rest_specification.json", "r") as f:
        app.openapi_schema = json.load(f)
    return app.openapi_schema

if SPEC_PATH:
    app.openapi = custom_openapi

import src.endpoints