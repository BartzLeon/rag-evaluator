from app.tasks import celery_app
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    celery_app.start()
