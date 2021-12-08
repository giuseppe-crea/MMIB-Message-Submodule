import os

from celery import Celery
from sqlalchemy.orm.exc import NoResultFound

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
            # message = Message().query.filter_by(id=int(message_id)).one()
            db.session.query(Message).filter(
                Message.id == message_id).update(dict(status=2))
            # message.status = 2
            # db.session.add(message)
            db.session.commit()
            eprint("Commit for message with id " + str(message_id) + " complete.")
            message = Message().query.filter_by(id=int(message_id)).first()
            eprint("Message with id" + str(message.get_id()) + " has status " + str(message.status))
        except Exception as e:
            eprint(str(e))
            pass  # this means the message was retracted
    return 0
