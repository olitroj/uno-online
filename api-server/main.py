import os
import json
from fastapi import FastAPI
from contextlib import asynccontextmanager

POSTGRES_USER   = os.environ.get("POSTGRES_USER")
POSTGRES_PASS   = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DB     = os.environ.get("POSTGRES_DB")
POSTGRES_HOST   = os.environ.get("POSTGRES_HOST")

from src.db import init_db_conn, close_db_conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    if POSTGRES_DB is not None and POSTGRES_USER is not None and POSTGRES_PASS is not None and POSTGRES_HOST is not None:
        await init_db_conn()
        yield
        await close_db_conn()
    else:
        yield

ENABLE_SWAGGER_UI = os.environ.get("ENABLE_SWAGGER_UI")

app = FastAPI(
    lifespan=lifespan,
    openapi_url="/openapi.json" if ENABLE_SWAGGER_UI else None,
    docs_url="/docs" if ENABLE_SWAGGER_UI else None,
    redoc_url="/redoc" if ENABLE_SWAGGER_UI else None,
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    with open("../docs/rest_specification.json", "r") as f:
        app.openapi_schema = json.load(f)
    return app.openapi_schema

if ENABLE_SWAGGER_UI:
    app.openapi = custom_openapi

import src.endpoints