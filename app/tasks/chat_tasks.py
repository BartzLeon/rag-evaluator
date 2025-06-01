import asyncio
from datetime import datetime
from app.tasks import celery_app
from app.db import async_session
from app.models import RatingResult, Testset, Document
from app.chat_models.factory import ChatModelFactory
from app.evaluate.evaluator_factory import EvaluatorFactory
from app.evaluate.giskart_evaluator import GiskartEvaluator
from app.evaluate.ragas_evaluator import RagasEvaluator
from app.testset_loader.qa_testset_loader import QATestsetLoader
from app.promt_templates.simple_prompt_template import SimplePromptTemplate
from app.document_loader.cached_documents_loader import CachedDocumentsLoader
from app.vectorestores.chroma_db_factory import ChromaDBFactory
from app.embeddings.factory import EmbeddingsFactory
from langchain_core.vectorstores import InMemoryVectorStore, VectorStore
from app.config.logging_config import task_logger
from langchain_core.documents import Document as LangchainDocument
from typing import Tuple, List, Optional, cast, Any
from langchain_core.embeddings import Embeddings as LangchainEmbeddings

@celery_app.task
def process_chat_request(request_data: dict):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_process_chat_request_async(request_data))
    else:
        loop.run_until_complete(_process_chat_request_async(request_data))

async def _process_chat_request_async(request_data: dict):
    async with async_session() as db:
        rating = None
        try:
            llm_to_be_evaluated_type = cast(str, request_data.get("llm_to_be_evaluated_type", "unknown"))
            judge_llm_type = cast(str, request_data.get("judge_llm_type", "unknown"))
            testset_id = cast(Optional[int], request_data.get("testset"))

            model_to_be_evaluated = ChatModelFactory.get_langchain_model(llm_to_be_evaluated_type)
            judge_llm = ChatModelFactory.get_langchain_model(judge_llm_type)
            
            rating = await create_rating(db, llm_to_be_evaluated_type, judge_llm_type, testset_id)

            if testset_id is None:
                task_logger.error("Testset ID is missing in the request.")
                rating.status = "Error"
                rating.report_path = "Testset ID is missing."
                await db.commit()
                return

            testset_model = await db.get(Testset, testset_id)
            if not testset_model:
                task_logger.error(f"Testset with ID {testset_id} not found.")
                rating.status = "Error"
                rating.report_path = f"Testset with ID {testset_id} not found."
                await db.commit()
                return
            
            testset_model_id = cast(int, testset_model.id)
            testset_document_id = cast(int, testset_model.document)

            test_set_loader = QATestsetLoader(f"app/data/testsets/{testset_model_id}.jsonl")
            
            documents, vectorstore, document_model_instance = await get_document_and_vectorstore(testset_document_id, db)

            if not document_model_instance or not documents:
                error_msg = f"Document data or model for dataset ID {testset_document_id} not found."
                task_logger.error(error_msg)
                rating.status = "Error"
                rating.report_path = error_msg
                await db.commit()
                return

            # Set start time for evaluation
            start_time = datetime.now()
            rating.start_eval = start_time
            await db.commit()
            task_logger.info(f"Evaluation started at: {start_time}")

            evaluator = EvaluatorFactory.get_model(
                #evaluator=GiskartEvaluator.__name__,
                evaluator=RagasEvaluator.__name__,
                testset_loader=test_set_loader,
                prompt_template=SimplePromptTemplate(),
                model_to_be_evaluated=model_to_be_evaluated,
                judge_llm=judge_llm,
                judge_llm_type=judge_llm_type,
                documents=documents,
                vectorstore=vectorstore,
                embedding_model=str(testset_model.embedding_model)
            )
            
            eval_result = evaluator.evaluate()
            
            # Set end time for evaluation
            end_time = datetime.now()
            rating.end_eval = end_time
            
            # Calculate duration in seconds
            duration = (end_time - start_time).total_seconds()
            rating.time_eval = duration
            
            task_logger.info(f"Evaluation completed at: {end_time}, Duration: {duration:.2f} seconds")
            
            if eval_result is None:
                error_msg = "Evaluator returned None, indicating an issue during evaluation."
                task_logger.error(error_msg)
                rating.status = "Error"
                rating.report_path = error_msg
                await db.commit()
                return
                
            report_path, scores, knowledge_base_score = eval_result
            task_logger.info(f"Report generated at path: {report_path}")

            rating.status = "Completed"
            rating.report_path = report_path
            if hasattr(scores, 'to_json') and callable(scores.to_json):
                rating.scores = scores.to_json()
            elif isinstance(scores, dict) or isinstance(scores, list):
                import json
                rating.scores = json.dumps(scores)
            else:
                rating.scores = None
            
            rating.knowledge_base_score = knowledge_base_score
            await db.commit()
            await db.refresh(rating)

            task_logger.info(f"Rating completed successfully with ID: {rating.id}")

        except Exception as e:
            task_logger.error(f"Error processing chat request: {e}", exc_info=True)
            if rating: 
                try:
                    # Set end time even for errors to track total time
                    if rating.start_eval and not rating.end_eval:
                        end_time = datetime.now()
                        rating.end_eval = end_time
                        duration = (end_time - rating.start_eval).total_seconds()
                        rating.time_eval = duration
                    
                    rating.status = "Error"
                    rating.report_path = str(e) 
                    await db.commit()
                except Exception as e2:
                    task_logger.error(f"Error updating rating status: {e2}")
            await db.rollback()

async def create_rating(db, llm_to_be_evaluated_type: str, judge_llm_type: str, testset_id: Optional[int] = None) -> RatingResult:
    rating = RatingResult(
        status="Processing", 
        llm_to_be_evaluated_type=llm_to_be_evaluated_type,
        judge_llm_type=judge_llm_type,
        testset_id=testset_id
    )
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    task_logger.info(f"New RatingResult created with ID: {rating.id}")
    return rating

async def get_document_and_vectorstore(dataset_id: int, db) -> Tuple[List[LangchainDocument], VectorStore, Optional[Document]]:
    document_model = await db.get(Document, dataset_id)
    if not document_model:
        raise ValueError(f"Document with ID {dataset_id} not found.")

    doc_id_str = str(cast(int, document_model.id))
    document_loader = CachedDocumentsLoader(url=doc_id_str)
    loaded_documents = document_loader.load_and_split()
    
    embedding_model_name = cast(str, document_model.embedding_model)
    embeddings = cast(LangchainEmbeddings, EmbeddingsFactory.get_embeddings("langchain/" + embedding_model_name))

    if not document_model.saved_to_chroma:
        task_logger.info(f"Using InMemoryVectorStore for document ID: {document_model.id}")
        vectorstore = ChromaDBFactory.from_documents(
            documents=loaded_documents,
            embedding=embeddings,
        )
    else:
        collection_name = cast(str, document_model.name)
        task_logger.info(f"Using ChromaDB for document ID: {document_model.id}, collection: {collection_name}")
        vectorstore = ChromaDBFactory.from_documents(
            collection_name=collection_name,
            embedding=embeddings,
        )
    return loaded_documents, vectorstore, document_model 