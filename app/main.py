from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.chat_models.factory import ChatModelFactory
from app.db import get_db
from app.dto.create_documents_dto import CreateDocumentsDTO
from app.dto.create_testset_dto import CreateTestsetDTO
from app.dto.file_dto import FileCreateDTO, FileReadDTO
from app.models import RatingResult, Document, Testset, DocumentRead
from app.models.file import UploadedFile
from app.models.association import file_document
from fastapi import FastAPI, APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app import db
from app.dto.process_request_dto import ProcessRequestDTO
from app.testset_loader.qa_testset_loader import QATestsetLoader
from app.websocket import websocket_endpoint
from app.tasks import process_chat_request, create_documents_request, create_testset_request
from dotenv import load_dotenv
from typing import List, Optional
import os
import shutil
from app.dto.source_dto import SourceDTO
from pydantic import BaseModel
from datetime import datetime

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3333"],  # Adjust this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = "app/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
async def get_all_ratings(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status"),
    llm_to_be_evaluated_type: Optional[str] = Query(None, description="Filter by LLM to be evaluated type"),
    judge_llm_type: Optional[str] = Query(None, description="Filter by judge LLM type"),
    testset_id: Optional[int] = Query(None, description="Filter by testset ID"),
    show_scores: Optional[bool] = Query(False, description="Whether to include scores in the response")
):
    try:
        query = select(RatingResult)
        
        # Apply filters if provided
        if status is not None:
            query = query.filter(RatingResult.status == status)
        if llm_to_be_evaluated_type is not None:
            query = query.filter(RatingResult.llm_to_be_evaluated_type == llm_to_be_evaluated_type)
        if judge_llm_type is not None:
            query = query.filter(RatingResult.judge_llm_type == judge_llm_type)
        if testset_id is not None:
            query = query.filter(RatingResult.testset_id == testset_id)
        
        query = query.order_by(RatingResult.id.desc())
        
        result = await db.execute(query)
        ratings = result.scalars().all()
        
        # Convert to dict and conditionally remove scores
        rating_dicts = []
        for rating in ratings:
            rating_dict = {
                "id": rating.id,
                "status": rating.status,
                "report_path": rating.report_path,
                "llm_to_be_evaluated_type": rating.llm_to_be_evaluated_type,
                "judge_llm_type": rating.judge_llm_type,
                "testset_id": rating.testset_id,
                "start_eval": rating.start_eval,
                "end_eval": rating.end_eval,
                "time_eval": rating.time_eval
            }
            if show_scores:
                rating_dict["scores"] = rating.scores
                rating_dict["knowledge_base_score"] = rating.knowledge_base_score
            rating_dicts.append(rating_dict)
            
        return rating_dicts
    except Exception as e:
        print(f"❌ Error fetching ratings: {e}")
        return []

@app.get("/documents/")
async def get_all_documents(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.files))
            .order_by(Document.id.desc())
        )
        documents = result.scalars().all()
        return [doc.to_read_model() for doc in documents]
    except Exception as e:
        print(f"❌ Error fetching documents: {e}")
        raise e

@app.post("/files/")
async def upload_file(
    uploaded_file: UploadFile = FastAPIFile(...),
    db: AsyncSession = Depends(get_db)
) -> FileReadDTO:
    try:
        if not uploaded_file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
            
        file_path = os.path.join(UPLOAD_DIR, str(uploaded_file.filename))
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(uploaded_file.file, buffer)

        file_record = UploadedFile(
            filename=uploaded_file.filename,
            file_path=file_path
        )
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)

        return FileReadDTO.from_orm(file_record)
    except Exception as e:
        print(f"❌ Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/")
async def get_files(db: AsyncSession = Depends(get_db)) -> List[FileReadDTO]:
    try:
        result = await db.execute(select(UploadedFile))
        files = result.scalars().all()
        return [FileReadDTO.from_orm(file) for file in files]
    except Exception as e:
        print(f"❌ Error fetching files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{file_id}")
async def delete_file(file_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(UploadedFile).filter(UploadedFile.id == file_id))
        file = result.scalars().first()
        if not file:
            raise HTTPException(status_code=404, detail="File not found")

        # Delete physical file
        file_path = str(file.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete database record
        await db.delete(file)
        await db.commit() 

        return {"message": "File deleted successfully"}
    except Exception as e:
        print(f"❌ Error deleting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/")
async def create_document(
    document_dto: CreateDocumentsDTO,
    db: AsyncSession = Depends(get_db)
):
    try:
        document = Document(
            name=document_dto.name,
            embedding_model=document_dto.embedding_model,
            repos=document_dto.repos or [],
        )
        db.add(document)
        await db.commit()
        await db.refresh(document)

        # Get sources from URLs
        sources = document_dto.get_sources()

        # Add file sources if file_ids are provided in the DTO
        if document_dto.file_ids:
            # Load the files with their relationships
            result = await db.execute(
                select(UploadedFile)
                .filter(UploadedFile.id.in_(document_dto.file_ids))
                .options(selectinload(UploadedFile.documents))
            )
            files = result.scalars().all()
            
            # Verify all files exist
            if len(files) != len(document_dto.file_ids):
                found_ids = {int(str(file.id)) for file in files}
                missing_ids = set(document_dto.file_ids) - found_ids
                raise HTTPException(status_code=404, detail=f"Files with ids {missing_ids} not found")
            
            # Add files to document and create sources
            for file in files:
                # Add the relationship through the association table
                await db.execute(
                    insert(file_document).values(
                        file_id=file.id,
                        document_id=document.id
                    )
                )
                sources.append(SourceDTO.create_file_source(str(file.file_path)))

        await db.commit()

        # Create request data with all sources
        request_data = {
            "name": document_dto.name,
            "sources": [source.model_dump() for source in sources],
            "embedding_model": document_dto.embedding_model
        }

        task = create_documents_request.delay(request_data, document.id)
        return {"message": "Data received", "task_id": task.id, "document_id": document.id}
    except Exception as e:
        raise e
        print(f"❌ Error creating document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/testsets/")
async def get_all_test_sets(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Testset)
            .order_by(Testset.id.desc())
        )
        test_sets = result.scalars().all()
        return test_sets
    except Exception as e:
        print(f"❌ Error fetching test sets: {e}")
        return []

@app.get("/testsets/{testset_id}")
async def get_test_set(testset_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Testset).filter(Testset.id == testset_id))
        test_set = result.scalars().first()
        if test_set:
            test_set_loader = QATestsetLoader(f"app/data/testsets/{test_set.id}.jsonl")
            test_set_content = test_set_loader.load()
            test_set.questions = test_set_content.to_pandas().to_json()
        return test_set
    except Exception as e:
        print(f"❌ Error fetching test set: {e}")
        return []

@app.post("/testsets/")
async def create_test_set(testset_dto: CreateTestsetDTO, db: AsyncSession = Depends(get_db)):
    try:
        test_set = Testset(
            name=testset_dto.name,
            model_type=testset_dto.model_type,
            embedding_model=testset_dto.embedding_model,
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

@app.get('/models/')
async def get_models():
    return ChatModelFactory.available_models()

@app.get('/repos/')
async def get_available_repos():
    """Get list of available git repositories in data/repos folder"""
    try:
        repos_dir = "app/data/repos"
        if not os.path.exists(repos_dir):
            return []
        
        repos = []
        for item in os.listdir(repos_dir):
            repo_path = os.path.join(repos_dir, item)
            if os.path.isdir(repo_path):
                # Check if it's a git repository by looking for .git folder
                git_path = os.path.join(repo_path, '.git')
                if os.path.exists(git_path):
                    repos.append({
                        "name": item,
                        "path": repo_path,
                        "is_git_repo": True
                    })
                else:
                    repos.append({
                        "name": item,
                        "path": repo_path,
                        "is_git_repo": False
                    })
        
        return repos
    except Exception as e:
        print(f"❌ Error fetching repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

router = APIRouter()

app.websocket("/ws")(websocket_endpoint)
