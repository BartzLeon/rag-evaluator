import asyncio
import pandas as pd
from app.tasks import celery_app
from app.db import async_session
from app.models import Testset, Document
from app.document_loader.cached_documents_loader import CachedDocumentsLoader
from giskard.rag import KnowledgeBase
from giskard.llm.client.litellm import LiteLLMClient
from giskard.rag import generate_testset
from app.config.logging_config import task_logger
from app.chat_models.factory import ChatModelFactory
from app.embeddings.factory import EmbeddingsFactory
from app.embeddings.giskard.factory import GiskardEmbeddingsFactory
from app.decorator.generate_testsset_decorator import with_testset_callbacks

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
            
            if not testset_model or not document_model:
                raise ValueError("Testset or Document not found")

            testset_model.status = "Processing"
            await db.commit()

            documents = CachedDocumentsLoader(document_model.id).load_and_split()

            df = pd.DataFrame([d.page_content for d in documents], columns=["text"])

            # Use the specified model types from the testset model
            model_type = testset_model.model_type
            embedding_model = testset_model.embedding_model
            
            # Configure the global models
            ChatModelFactory.set_global_llm_model(model_type)
            GiskardEmbeddingsFactory.set_global_embedding_model(embedding_model)

            knowledge_base = KnowledgeBase(df)

            from tqdm import tqdm
            
            def progress_callback(event: str, data: dict):
                if event == "progress":
                    print(f"-------------Progress: {data['current']}/{data['total']} ({data['current']/data['total']*100:.1f}%)")
                else:
                    print(f"-------------{event}: {data}")

            @with_testset_callbacks(callback=progress_callback)
            def my_testset(*args, **kwargs):
                return generate_testset(*args, **kwargs)

            testset = my_testset(
                knowledge_base,
                num_questions=testset_model.num_questions,
                agent_description=testset_model.agent_description,
            )

            ChatModelFactory.reset_global_llm_model()
            GiskardEmbeddingsFactory.reset_global_embedding_model()

            # Save the testset
            output_path = f"app/data/testsets/{testset_model.id}.jsonl"
            testset.save(output_path)
            task_logger.info(f"Testset saved to {output_path}")

            testset_model.status = "Finished"
            await db.commit()
            await db.refresh(testset_model)

        except Exception as e:
            if testset_model:
                testset_model.status = "Error"
                await db.commit()
                await db.refresh(testset_model)

            task_logger.error(f"Error creating test set: {e}")

            ChatModelFactory.reset_global_llm_model()
            GiskardEmbeddingsFactory.reset_global_embedding_model()
            
            raise e 