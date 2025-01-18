from celery import Celery
import os
from dotenv import load_dotenv
import logging
from app.DocumnetLoader.CachedDocumentsLoader import CachedDocumentsLoader
from app.chat_models.factory import ChatModelFactory
from app.db import async_session
from app.evaluate.EvaluatorFactory import EvaluatorFactory
from app.evaluate.RagasEvaluator import RagasEvaluator
from app.models import RatingResult
from app.promt_templates.SimplePromptTemplate import SimplePromptTemplate
from app.testset_loader.QATestsetLoader import QATestsetLoader
from app.vectorestores.ChromaDBFactory import ChromaDBFactory

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

async def _process_chat_request_async(request_data: dict):
    async with async_session() as db:
        try:
            model_type = request_data.get("model_type", "unknown")

            # Get the model
            model = ChatModelFactory.get_model(model_type)
            rating = RatingResult(status="Processing", model_type=model_type)
            db.add(rating)
            await db.commit()
            await db.refresh(rating)
            print(f"✅ New RatingResult created with ID: {rating.id}")
            print(RagasEvaluator.__name__)


            evaluator = EvaluatorFactory.get_model(
                evaluator=RagasEvaluator.__name__,
                testset_loader = QATestsetLoader('app/data/testsets/test-set.jsonl'),
                prompt_template= SimplePromptTemplate(),
                model=model,
                document_loader= CachedDocumentsLoader('app/data/documents/ml-school.pkl'),
                vectorstore_factory= ChromaDBFactory()
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