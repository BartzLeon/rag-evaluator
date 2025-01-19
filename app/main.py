from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.dto.create_documents_dto import CreateDocumentsDTO
from app.dto.create_testset_dto import CreateTestsetDTO
from app.models import RatingResult, Document, Testset
from fastapi import FastAPI, APIRouter, Depends
from app import db
from app.dto.process_request_dto import ProcessRequestDTO
from app.websocket import websocket_endpoint
from app.tasks import process_chat_request, create_documents_request, create_testset_request
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

@app.get("/ratings/") #response_model=List[RatingResultRead]
async def get_all_ratings(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(RatingResult))
        ratings = result.scalars().all()
        return ratings
    except Exception as e:
        print(f"❌ Error fetching ratings: {e}")
        return []

@app.get("/documents/") #response_model=List[RatingResultRead]
async def get_all_ratings(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Document))
        documents = result.scalars().all()
        return documents
    except Exception as e:
        print(f"❌ Error fetching documents: {e}")
        return []

@app.post("/documents/")
async def create_document(document_dto: CreateDocumentsDTO, db: AsyncSession = Depends(get_db)):
    try:
        document = Document(
            name=document_dto.name,
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        task = create_documents_request.delay(document_dto.model_dump(), document.id)
        return {"message": "Data received", "task_id": task.id, "document_id": document.id}
    except Exception as e:
        print(f"❌ Error creating document: {e}")
        raise e
        return {"error": str(e)}

@app.get("/testsets/")
async def get_all_test_sets(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Testset))
        test_sets = result.scalars().all()
        return test_sets
    except Exception as e:
        print(f"❌ Error fetching test sets: {e}")
        return []

@app.post("/testsets/")
async def create_test_set(testset_dto: CreateTestsetDTO, db: AsyncSession = Depends(get_db)):
    try:
        test_set = Testset(
            name=testset_dto.name,
            model_type=testset_dto.model_type,
            document=testset_dto.document,
            num_questions=testset_dto.num_questions,
            agent_description=testset_dto.agent_description,
        )
        db.add(test_set)
        await db.commit()
        await db.refresh(test_set)

        task = create_testset_request.delay(testset_dto.model_dump(), test_set.id)

        return {"message": "Test set created", "test_set_id": test_set.id, "task_id": task.id}
    except Exception as e:
        print(f"❌ Error creating test set: {e}")
        raise e
        return {"error": str(e)}


router = APIRouter()

app.websocket("/ws")(websocket_endpoint)
