from message_server.database import db, Message


# this method assumes values have been previously checked and are safe
def delete_for_receiver(message_query: Message):
    message_query.visible_to_receiver = False
    if not message_query.visible_to_sender:
        db.session.delete(message_query)
    db.session.commit()


def delete_for_sender(message_query: Message):
    message_query.visible_to_sender = False
    if not message_query.visible_to_receiver:
        db.session.delete(message_query)
    db.session.commit()
