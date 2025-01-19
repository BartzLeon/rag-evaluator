import time
from celery import Celery
import pickle
import os
from dotenv import load_dotenv
import logging

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

from app.document_loader.cached_documents_loader import CachedDocumentsLoader
from app.chat_models.factory import ChatModelFactory
from app.db import async_session
from app.document_loader.web_base_loader_and_splitter import WebBaseLoaderAndSplitter
from app.evaluate.evaluator_factory import EvaluatorFactory
from app.evaluate.giskart_evaluator import GiskartEvaluator
from app.evaluate.ragas_evaluator import RagasEvaluator
from app.models import RatingResult, DocumentCreate, Document
from app.promt_templates.simple_prompt_template import SimplePromptTemplate
from app.testset_loader.qa_testset_loader import QATestsetLoader
from app.vectorestores.chroma_db_factory import ChromaDBFactory

load_dotenv()
logging.getLogger("httpx").setLevel(logging.WARNING)

BROKER_URL = os.getenv("CELERY_BROKER_URL")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "worker",
    broker=BROKER_URL,
    backend=RESULT_BACKEND
)

@celery_app.task
def process_chat_request(request_data: dict):
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_process_chat_request_async(request_data))
    else:
        loop.run_until_complete(_process_chat_request_async(request_data))

@celery_app.task
def create_documents_request(request_data: dict, document_id: id):
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_create_documents_async(request_data, document_id))
    else:
        loop.run_until_complete(_create_documents_async(request_data, document_id))

@celery_app.task
def create_testset_request(request_data: dict):
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_create_testset_async(request_data))
    else:
        loop.run_until_complete(_create_testset_async(request_data))

async def _create_documents_async(request_data: dict, document_id: int):
    async with async_session() as db:
        document = await db.get(Document, document_id)

        document.status = "Processing"
        await db.commit()

        try:
            documents = []

            for source in request_data["sources"]:
                url = source["url"]
                print(f"Processing URL: {url}")
                loader = WebBaseLoaderAndSplitter(url=url)
                documents.extend(loader.load_and_split())

            document.status = "Downloaded"
            await db.commit()
            await db.refresh(document)

            with open(f"app/data/documents/{document.id}.pkl", "wb") as f:
                pickle.dump(documents, f)

            document.status = "Saved"
            await db.commit()
            await db.refresh(document)

            time.sleep(5)

            document.status = "Indexing"
            await db.commit()
            await db.refresh(document)

            ChromaDBFactory.from_documents(
                documents=documents,
                collection_name=document.name,
            )

            document.saved_to_chroma = True
            document.status = "Finished"
            await db.commit()
            await db.refresh(document)

        except Exception as e:
            document.status = "Error"
            await db.commit()
            await db.refresh(document)

            print(f"❌ Error creating document: {e}")
            raise e

async def _process_chat_request_async(request_data: dict):
    async with async_session() as db:
        try:
            model_type = request_data.get("model_type", "unknown")
            dataset_id = request_data.get("dataset", None)

            # Get the model
            model = ChatModelFactory.get_model(model_type)
            rating = RatingResult(status="Processing", model_type=model_type)
            db.add(rating)
            await db.commit()
            await db.refresh(rating)
            print(f"✅ New RatingResult created with ID: {rating.id}")

            if dataset_id is None:
                rating.status = "Error"
                await db.commit()

                return

            document = await db.get(Document, dataset_id)
            document_loader = CachedDocumentsLoader(document.name)



            if not document.saved_to_chroma:
                vectorstore = InMemoryVectorStore.from_documents(
                    documents=document_loader.load_and_split(),
                    embedding=OpenAIEmbeddings()
                )
            else:
                vectorstore = ChromaDBFactory.from_documents(
                    collection_name=document.name
                )

            test_set_loader = None

            evaluator = EvaluatorFactory.get_model(
                evaluator=GiskartEvaluator.__name__,
                testset_loader = QATestsetLoader('app/data/testsets/test-set.jsonl'),
                prompt_template= SimplePromptTemplate(),
                model=model,
                document_loader=document_loader,
                vectorstore_factory= vectorstore
            )

            report_path, scores, knowledge_base_score = evaluator.evaluate()

            print(f"Report Path: {report_path}")

            rating.status = "Completed"
            rating.report_path = report_path
            rating.scores = scores.to_json()
            rating.knowledge_base_score = knowledge_base_score
            await db.commit()
            await db.refresh(rating)

            print(f"✅ Rating completed with ID: {rating.id}")

        except Exception as e:
            try:
                rating.status = "Error"
                await db.commit()
            except Exception as e2:
                print(f"❌ Error updating rating status: {e2}")


            await db.rollback()
            raise e



