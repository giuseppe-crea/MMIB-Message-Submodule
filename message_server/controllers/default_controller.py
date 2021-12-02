import connexion
import pytz
import six

from datetime import datetime

from flask import jsonify
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from message_server.models.draft import Draft  # noqa: E501
from message_server.models.message import Message  # noqa: E501
from message_server import util
from message_server.tasks import deliver_message
import message_server.blacklist as bl
from message_server.database import Message as DB_Message, db


def add_blacklist(owner, email):  # noqa: E501
    """add to user blacklist

    Receive a (owner, email), add the email to the owner&#39;s blacklist.  # noqa: E501

    :param owner: owner of the blacklist
    :type owner: str
    :param email: address to check
    :type email: str

    :rtype: None
    """
    bl.add2blacklist_local(owner, email)
    return None, 200


def check_blacklist(owner, email):  # noqa: E501
    """check the user blacklist

    Receive a (owner, email), check if email is present in owner&#39;s blacklist.  # noqa: E501

    :param owner: owner of the blacklist
    :type owner: str
    :param email: address to check
    :type email: str

    :rtype: None
    """
    if bl.is_blacklisted(email, owner):
        return None, 200
    else:
        return None, 404


def create_draft(data):  # noqa: E501
    """create draft

    Create a new draft.  # noqa: E501

    :param data: draft data
    :type data: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        data = Message.from_dict(connexion.request.get_json())  # noqa: E501
        if data.image_hash is not None and data.image_hash != '' and \
                len(data.image_hash) > 10240:
            return None, 400
        message = DB_Message()
        message.add_message(
            data.message,
            data.sender_mail,
            data.receiver_mail,
            data.time,
            data.image,
            data.image_hash,
            0,
            True
        )
        db.session.add(message)
        db.session.commit()
        return None, 200
    else:
        return None, 400


def delete_draft(id):  # noqa: E501
    """delete a draft

    Deletes a draft.  # noqa: E501

    :param id: draft id
    :type id: int

    :rtype: None
    """
    DB_Message.query.filter_by(id=id).delete()
    db.session.commit()

    return None, 200


def delete_message(email, id):  # noqa: E501
    """delete a message

    Hide a message referenced by id to the caller,  the mail of the caller is also needed.  # noqa: E501

    :param email: email of the requested
    :type email: str
    :param id: id of the message
    :type id: int

    :rtype: None
    """
    try:
        message = DB_Message.query.filter_by(id=id).one()
    except NoResultFound:
        return None, 400
    # print(message.receiver_mail)
    if message.receiver_email == email:
        from message_server.delete import delete_for_receiver
        delete_for_receiver(message)
    elif message.sender_email == email:
        from message_server.delete import delete_for_sender
        delete_for_sender(message)
    else:
        return None, 400
    return None, 200


def edit_draft(data):  # noqa: E501
    """edit a draft

    Edit a draft, the body must contain an id field.  # noqa: E501
    ALL FIELDS WILL BE REPLACED

    :param data: draft data
    :type data: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        data = Draft.from_dict(connexion.request.get_json())  # noqa: E501
        try:
            message = DB_Message.query.filter_by(
                id=data.id,
                sender_email=data.sender_mail,
                status=0
            ).one()
        except NoResultFound:
            return None, 400
        if data.image_hash is not None and data.image_hash != '' and \
                len(data.image_hash) > 10240:
            return None, 400
        message.add_message(
            data.message,
            data.sender_mail,
            data.receiver_mail,
            data.time,
            data.image,
            data.image_hash,
            0,
            True
        )
        db.session.commit()
    return None, 200


def get_blacklist(owner):  # noqa: E501
    """get the user&#39;s blacklist

    Get the blacklist of the user.  # noqa: E501

    :param owner: owner&#39;s email
    :type owner: str

    :rtype: List[str]
    """
    ret_list = bl.blacklist_for_user(owner)
    if len(ret_list) > 0:
        return jsonify(ret_list)
    else:
        return None, 404


def query_wrangler(query):
    reply = []
    if query is None:
        return None, 200
    else:
        for row in query:
            reply_row = Message(
                row.id,
                row.sender_email,
                row.receiver_email,
                row.message,
                row.time,
                row.image,
                row.image_hash
            )
            reply.append(reply_row)
        return jsonify(reply)


def get_drafts(owner):  # noqa: E501
    """get the user&#39;s drafts list

    Get the drafts of the users.  # noqa: E501

    :param owner: owner&#39;s email
    :type owner: str

    :rtype: List[Message]
    """
    drafts = DB_Message.query.filter_by(sender_email=owner, status=0)
    return query_wrangler(drafts)


def get_inbox(owner):  # noqa: E501
    """get the user&#39;s inbox

    Get the inbox of the users.  # noqa: E501

    :param owner: owner&#39;s email
    :type owner: str

    :rtype: List[Message]
    """
    inbox = DB_Message.query.filter_by(
        receiver_email=owner,
        status=2,
        visible_to_receiver=True
    )
    return query_wrangler(inbox)


def get_outbox(owner):  # noqa: E501
    """get the user&#39;s outbox

    Get the outbox of the users.  # noqa: E501

    :param owner: owner&#39;s email
    :type owner: str

    :rtype: List[Message]
    """
    outbox = DB_Message.query.filter(
        DB_Message.sender_email == owner,
        DB_Message.status.in_([1, 2]),
        DB_Message.visible_to_sender
    ).all()
    return query_wrangler(outbox)


def remove_blacklist(owner, email):  # noqa: E501
    """remove from user blacklist

    Receive a (owner, email), remove the email from the owner&#39;s blacklist.  # noqa: E501

    :param owner: owner of the blacklist
    :type owner: str
    :param email: owner of the blacklist
    :type email: str

    :rtype: None
    """
    return bl.remove_from_blacklist(owner, email)


def send_message(data):  # noqa: E501
    """send a message

    Send a message.  # noqa: E501
    receiver_mail is a comma separated list of strings in a string
    these mails are guaranteed to exist

    :param data: message data, if an id is present, the message is a pre-existing draft.
    :type data: dict | bytes

    :rtype: int array
    """
    sent = []
    if connexion.request.is_json:
        data = Message.from_dict(connexion.request.get_json())  # noqa: E501
        time_aware = pytz.timezone('Europe/Rome').localize(
            datetime.strptime(data.time, '%Y-%m-%d %H:%M:%S')
        )
        # give minute precision for message send operation
        # this will send any message targeted for the current minute instantly
        minute_precision = datetime.now(
            pytz.timezone('Europe/Rome')
        ).replace(second=0, microsecond=0)
        if time_aware >= minute_precision:
            # checks on the validity of data.image happen within Message object
            if data.image_hash is not None and data.image_hash != '' and \
                    len(data.image_hash) > 10240:
                return [-1]
            to_parse = data.receiver_mail.split(',')
            for address in to_parse:
                address = address.strip()
                # image has been saved on volume by the gateway
                # content filter is checked on read by the gateway
                message = DB_Message()
                # check blacklist
                if bl.is_blacklisted(data.sender_mail, address):
                    visible_to_receiver = False
                else:
                    visible_to_receiver = True
                message.add_message(
                    data.message,
                    data.sender_mail,
                    address,
                    data.time,
                    data.image,
                    data.image_hash,
                    1,
                    visible_to_receiver
                )
                db.session.add(message)
                db.session.commit()
                sent.append(message.get_id())
                deliver_message.apply_async(
                    (message.get_id(),),
                    eta=time_aware
                )
        else:
            sent = [-1]
    return sent


def set_as_read(id):  # noqa: E501
    """set as read

    Set a message as read  # noqa: E501

    :param id: message id
    :type id: str

    :rtype: None
    """
    id = int(id)
    try:
        message = DB_Message.query.filter_by(id=id).one()
    except NoResultFound:
        return None, 404
    message.is_read = True
    db.session.commit()
    return None, 200


def withdraw(id):  # noqa: E501
    """withdraw a message

    Withdraw a pending message using lottery points.  # noqa: E501

    :param id: message id
    :type id: str

    :rtype: None
    """
    id = int(id)
    try:
        message = DB_Message.query.filter_by(id=id).one()
    except NoResultFound:
        return None, 404
    db.session.delete(message)
    db.session.commit()
    return None, 200
