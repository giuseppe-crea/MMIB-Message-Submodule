import json

import connexion
import pytz
import six

from datetime import datetime
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
    :param email: owner of the blacklist
    :type email: str

    :rtype: None
    """
    return 'do some magic!'


def check_blacklist(data):  # noqa: E501
    """check the user blacklist

    Receive a (owner, email), check if email is present in owner&#39;s blacklist.  # noqa: E501

    :param data: (owner, email)
    :type data: str

    :rtype: None
    """
    return 'do some magic!'


def create_draft(data):  # noqa: E501
    """create draft

    Create a new draft.  # noqa: E501

    :param data: draft data
    :type data: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        data = Message.from_dict(connexion.request.get_json())  # noqa: E501

    return 'do some magic!'


def delete_draft(id):  # noqa: E501
    """delete a draft

    Create a new draft.  # noqa: E501

    :param id: draft id
    :type id: int

    :rtype: None
    """
    return 'do some magic!'


def delete_message(email, id):  # noqa: E501
    """delete a message

    Hide a message referenced by id to the caller,  the mail of the caller is also needed.  # noqa: E501

    :param email: email of the requested
    :type email: str
    :param id: id of the message
    :type id: int

    :rtype: None
    """
    return 'do some magic!'


def edit_draft(data):  # noqa: E501
    """edit a draft

    Edit a draft, the body must contain an id field.  # noqa: E501

    :param data: draft data
    :type data: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        data = Draft.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def get_blacklist(owner):  # noqa: E501
    """get the user&#39;s blacklist

    Get the blacklist of the user.  # noqa: E501

    :param owner: owner&#39;s email
    :type owner: str

    :rtype: List[str]
    """
    return 'do some magic!'


def get_drafts(owner):  # noqa: E501
    """get the user&#39;s drafts list

    Get the drafts of the users.  # noqa: E501

    :param owner: owner&#39;s email
    :type owner: str

    :rtype: List[Message]
    """
    return 'do some magic!'


def get_inbox(owner):  # noqa: E501
    """get the user&#39;s inbox

    Get the inbox of the users.  # noqa: E501

    :param owner: owner&#39;s email
    :type owner: str

    :rtype: List[Message]
    """
    return 'do some magic!'


def get_outbox(owner):  # noqa: E501
    """get the user&#39;s outbox

    Get the outbox of the users.  # noqa: E501

    :param owner: owner&#39;s email
    :type owner: str

    :rtype: List[Message]
    """
    return 'do some magic!'


def remove_blacklist(owner, email):  # noqa: E501
    """remove from user blacklist

    Receive a (owner, email), remove the email from the owner&#39;s blacklist.  # noqa: E501

    :param owner: owner of the blacklist
    :type owner: str
    :param email: owner of the blacklist
    :type email: str

    :rtype: None
    """
    return 'do some magic!'


def send_message(data):  # noqa: E501
    """send a message

    Send a message.  # noqa: E501
    receiver_mail is a comma separated list of strings in a string
    these mails are guaranteed to exist

    :param data: message data, if an id is present, the message is a pre-existing draft.
    :type data: dict | bytes

    :rtype: int
    """
    sent = []
    if connexion.request.is_json:
        data = Message.from_dict(connexion.request.get_json())  # noqa: E501
        time_aware = pytz.timezone('Europe/Rome').localize(datetime.strptime(data.time, '%Y-%m-%d %H:%M:%S'))
        to_parse = data.receiver_mail.split(',')
        for address in to_parse:
            address = address.strip()
            # image has been saved on volume by the gateway
            # content filter is checked on read by the gateway
            message = DB_Message()
            # check blacklist
            if bl.is_blacklisted(data.sender_mail, data.receiver_mail):
                visible_to_receiver = False
            else:
                visible_to_receiver = True
            message.add_message(
                data.message,
                data.sender_mail,
                address,
                data.time,
                data.image,
                1,
                visible_to_receiver
            )
            db.session.add(message)
            db.session.commit()
            sent.append(message.get_id())
            deliver_message.apply_async((message.get_id(),), eta=time_aware)
    return sent


def set_as_read(id):  # noqa: E501
    """set as read

    Set a message as read  # noqa: E501

    :param id: message id
    :type id: str

    :rtype: None
    """
    return 'do some magic!'


def withdraw(id):  # noqa: E501
    """withdraw a message

    Withdraw a pending message using lottery points.  # noqa: E501

    :param id: message id
    :type id: str

    :rtype: None
    """
    return 'do some magic!'
