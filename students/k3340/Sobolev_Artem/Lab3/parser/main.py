import asyncio
from contextlib import asynccontextmanager

import asyncpg
import requests
from fastapi import FastAPI, HTTPException

from config import PARSER_DB_URL
from schemas import ParseRequest, ParseResponse
from service import load_and_parse, save_book


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(
        dsn=PARSER_DB_URL,
        min_size=1,
        max_size=5,
    )
    try:
        yield
    finally:
        await app.state.db_pool.close()


app = FastAPI(
    title="Parser Service",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/parse", response_model=ParseResponse)
async def parse(request: ParseRequest) -> ParseResponse:
    try:
        book = await asyncio.to_thread(load_and_parse, str(request.url))
        created = await save_book(app.state.db_pool, book)
    except requests.RequestException as exception:
        raise HTTPException(status_code=502, detail=str(exception)) from exception
    except ValueError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
    except asyncpg.PostgresError as exception:
        raise HTTPException(status_code=500, detail=str(exception)) from exception

    return ParseResponse(
        message="Parsing completed",
        title=book.title,
        genre=book.genre,
        created=created,
    )
