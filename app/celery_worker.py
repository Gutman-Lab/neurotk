from celery import Celery
from os import getenv

celery_app = Celery(
    "tasks",
    broker=getenv("CELERY_BROKER_URL"),
    backend=getenv("CELERY_RESULT_BACKEND"),
)


@celery_app.task
def hello_world():
    return "Hello, World!"
