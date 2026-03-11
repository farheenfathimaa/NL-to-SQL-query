from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sql_chain import run_query
import os

from models import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    init_db()
    yield
    # (Cleanup code, if any, goes after yield)


app = FastAPI(title="NL to SQL Query Assistant", lifespan=lifespan)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    query: str
    result: str = None
    explanation: str = None
    error: str = None
    status: str


@app.get("/")
async def health_check():
    return {"status": "healthy"}


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    result = run_query(request.question)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
