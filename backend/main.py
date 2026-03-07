from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sql_chain import run_query
import os

from models import init_db

app = FastAPI(title="NL to SQL Query Assistant")

@app.on_event("startup")
def startup_event():
    init_db()

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
