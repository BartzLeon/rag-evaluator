from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from typing import List
from app.db import get_db
from app.models import RatingResult, RatingResultRead
from fastapi import FastAPI, WebSocket, BackgroundTasks, Request, APIRouter, Depends
from app import models, db, tasks
from app.dto.process_request_dto import ProcessRequestDTO
from app.websocket import websocket_endpoint
from app.tasks import process_chat_request
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.on_event("startup")
async def startup():
    await db.init_db()

@app.get("/")
def read_root():
    return {"message": "FastAPI with Docker, Celery, PostgreSQL, Redis"}

@app.post("/process/")
async def process_data(request: ProcessRequestDTO):
    try:
        task = process_chat_request.delay(request.model_dump())
        return {"message": "Data received", "task_id": task.id}
    except Exception as e:
        return {"error": str(e)}

router = APIRouter()

@app.get("/ratings/") #response_model=List[RatingResultRead]
async def get_all_ratings(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(RatingResult))
        ratings = result.scalars().all()
        return ratings
    except Exception as e:
        print(f"❌ Error fetching ratings: {e}")
        return []

app.websocket("/ws")(websocket_endpoint)
