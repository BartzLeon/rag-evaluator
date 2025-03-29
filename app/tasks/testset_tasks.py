import asyncio
import pandas as pd
from app.tasks import celery_app
from app.db import async_session
from app.models import Testset, Document
from app.document_loader.cached_documents_loader import CachedDocumentsLoader
from giskard.rag import KnowledgeBase
from giskard.llm.client.litellm import LiteLLMClient
from giskard.rag import generate_testset
from app.logging_config import task_logger
from app.chat_models.factory import ChatModelFactory
from app.embeddings.factory import EmbeddingsFactory

@celery_app.task
def create_testset_request(request_data: dict, testset_id: int):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_create_testset_async(request_data, testset_id))
    else:
        loop.run_until_complete(_create_testset_async(request_data, testset_id))

async def _create_testset_async(testset_data: dict, testset_id: int):
    async with async_session() as db:
        try:
            document_id = testset_data.get("document", None)
            testset_model = await db.get(Testset, testset_id)
            document_model = await db.get(Document, document_id)

            testset_model.status = "Processing"
            await db.commit()

            documents = CachedDocumentsLoader(document_model.id).load_and_split()

            df = pd.DataFrame([d.page_content for d in documents], columns=["text"])

            ChatModelFactory.set_global_llm_model("ollama/deepseek-r1:7b")

            embeddings = EmbeddingsFactory.get_embeddings("giskard/ollama/nomic-embed-text:latest")
            knowledge_base = KnowledgeBase(
                df,
                llm_client=ChatModelFactory.get_lite_llm_model(model_type="giskard/" + testset_model.model_type),
                embedding_model=embeddings
            )

            testset = generate_testset(
                knowledge_base,
                num_questions=testset_model.num_questions,
                agent_description=testset_model.agent_description,
            )

            ChatModelFactory.reset_global_llm_model()

            testset.save(f"app/data/testsets/{testset_model.id}.jsonl")

            testset_model.status = "Finished"
            await db.commit()
            await db.refresh(testset_model)

        except Exception as e:
            testset_model.status = "Error"
            await db.commit()
            await db.refresh(testset_model)

            task_logger.error(f"Error creating test set: {e}")

            ChatModelFactory.reset_global_llm_model()
            raise e 