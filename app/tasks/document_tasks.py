import asyncio
import pickle
import time
from app.tasks import celery_app
from app.db import async_session
from app.models import Document
from app.document_loader.web_base_loader_and_splitter import WebBaseLoaderAndSplitter
from app.document_loader.file_loader_and_splitter import FileLoaderAndSplitter
from app.vectorestores.chroma_db_factory import ChromaDBFactory
from app.embeddings.factory import EmbeddingsFactory
from app.config.logging_config import task_logger

@celery_app.task
def create_documents_request(request_data: dict, document_id: int):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_create_documents_async(request_data, document_id))
    else:
        loop.run_until_complete(_create_documents_async(request_data, document_id))

async def _create_documents_async(request_data: dict, document_id: int):
    async with async_session() as db:
        document = await db.get(Document, document_id)
        if not document:
            raise ValueError(f"Document with id {document_id} not found")

        document.status = "Processing"
        await db.commit()

        try:
            documents = []

            for source in request_data["sources"]:
                source_type = source["type"]
                task_logger.info(f"Processing source of type: {source_type}")
                
                if source_type == "url":
                    url = source["url"]
                    task_logger.info(f"Processing URL: {url}")
                    loader = WebBaseLoaderAndSplitter(url=url)
                elif source_type == "file":
                    file_path = source["file_path"]
                    task_logger.info(f"Processing file: {file_path}")
                    loader = FileLoaderAndSplitter(file_path=file_path)
                else:
                    raise ValueError(f"Unknown source type: {source_type}")
                
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

            embeddings = EmbeddingsFactory.get_embeddings("langchain/" + document.embedding_model)

            ChromaDBFactory.from_documents(
                documents=documents,
                collection_name=document.name,
                embedding=embeddings,
            )

            document.saved_to_chroma = True
            document.status = "Finished"
            await db.commit()
            await db.refresh(document)

        except Exception as e:
            document.status = "Error"
            await db.commit()
            await db.refresh(document)

            task_logger.error(f"Error creating document: {e}")
            raise e 