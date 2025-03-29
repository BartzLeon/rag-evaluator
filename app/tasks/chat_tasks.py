import asyncio
from app.tasks import celery_app
from app.db import async_session
from app.models import RatingResult, Testset, Document
from app.chat_models.factory import ChatModelFactory
from app.evaluate.evaluator_factory import EvaluatorFactory
from app.evaluate.giskart_evaluator import GiskartEvaluator
from app.testset_loader.qa_testset_loader import QATestsetLoader
from app.promt_templates.simple_prompt_template import SimplePromptTemplate
from app.document_loader.cached_documents_loader import CachedDocumentsLoader
from app.vectorestores.chroma_db_factory import ChromaDBFactory
from app.embeddings.factory import EmbeddingsFactory
from langchain_core.vectorstores import InMemoryVectorStore
from app.logging_config import task_logger

@celery_app.task
def process_chat_request(request_data: dict):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_process_chat_request_async(request_data))
    else:
        loop.run_until_complete(_process_chat_request_async(request_data))

async def _process_chat_request_async(request_data: dict):
    async with async_session() as db:
        try:
            model_type = request_data.get("model_type", "unknown")
            testset_id = request_data.get("testset", None)

            # Get the model
            model = ChatModelFactory.get_langchain_model(model_type)
            rating = await create_rating(db, model_type)

            if testset_id is None:
                rating.status = "Error"
                await db.commit()
                return

            testset_model = await db.get(Testset, testset_id)
            test_set_loader = QATestsetLoader(f"app/data/testsets/{testset_model.id}.jsonl")

            document_loader, vectorstore = await get_vectorstore(testset_model.document, db)
            evaluator = EvaluatorFactory.get_model(
                evaluator=GiskartEvaluator.__name__,
                testset_loader=test_set_loader,
                prompt_template=SimplePromptTemplate(),
                model=model,
                document_loader=document_loader,
                vectorstore_factory=vectorstore
            )

            report_path, scores, knowledge_base_score = evaluator.evaluate()
            task_logger.info(f"Report generated at path: {report_path}")

            rating.status = "Completed"
            rating.report_path = report_path
            rating.scores = scores.to_json()
            rating.knowledge_base_score = knowledge_base_score
            await db.commit()
            await db.refresh(rating)

            task_logger.info(f"Rating completed successfully with ID: {rating.id}")

        except Exception as e:
            try:
                rating.status = "Error"
                await db.commit()
            except Exception as e2:
                task_logger.error(f"Error updating rating status: {e2}")

            await db.rollback()
            raise e

async def create_rating(db, model_type):
    rating = RatingResult(status="Processing", model_type=model_type)
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    task_logger.info(f"New RatingResult created with ID: {rating.id}")
    return rating

async def get_vectorstore(dataset_id, db):
    document_model = await db.get(Document, dataset_id)
    document_loader = CachedDocumentsLoader(document_model.id)
    if not document_model.saved_to_chroma:
        embeddings = EmbeddingsFactory.get_embeddings("lite_llm/nomic-embed-text:latest")
        vectorstore = InMemoryVectorStore.from_documents(
            documents=document_loader.load_and_split(),
            embedding=embeddings,
        )
    else:
        vectorstore = ChromaDBFactory.from_documents(
            collection_name=document_model.name
        )
    return document_loader, vectorstore 