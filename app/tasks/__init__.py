from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

BROKER_URL = os.getenv("CELERY_BROKER_URL")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

celery_app = Celery(
    "worker",
    broker=BROKER_URL,
    backend=RESULT_BACKEND
)

from app.tasks.chat_tasks import process_chat_request
from app.tasks.document_tasks import create_documents_request, import_document_request
from app.tasks.testset_tasks import create_testset_request

__all__ = [
    'celery_app',
    'process_chat_request',
    'create_documents_request',
    'import_document_request',
    'create_testset_request'
] 