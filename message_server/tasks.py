from celery import Celery
from message_server.database import db


BACKEND = BROKER = 'redis://localhost:6379/0'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)
_APP = None


def give_context(app):
    global _APP
    _APP = app


@celery.task
def hello_world():
    if _APP is None:
        print("Oh no...")
    else:
        print("Hello world!")
    return
