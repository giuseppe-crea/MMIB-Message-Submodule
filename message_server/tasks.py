import os

from celery import Celery

from message_server.database import db, Message
from message_server.util import eprint


if os.environ.get('DOCKER') is not None:
    BACKEND = BROKER = 'redis://redis_messages:6378/0'
else:
    BACKEND = BROKER = 'redis://localhost:6379/0'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)
_APP = None


def do_task():
    global _APP
    if _APP is None:
        from message_server.__main__ import main
        _APP = main().app


@celery.task
def deliver_message(message_id):
    do_task()
    with _APP.app_context():
        # find the message with that given id
        try:
            db.session.query(Message).filter(
                Message.id == message_id).update(dict(status=2))
            db.session.commit()
        except Exception as e:
            eprint(str(e))
            pass  # this means the message was retracted
    return 0
