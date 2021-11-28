# some checks for the add functionality
from message_server.database import Blacklist, db


def _check_already_blocked(user, email):
    return db.session.query(
        Blacklist.query.filter(
            Blacklist.email == email,
            Blacklist.owner == user).exists()).scalar()


def _check_itself(user, email):
    return user == email


def _check_add_blacklist(user, email):
    return not (_check_already_blocked(user, email) or
                _check_itself(user, email))


def add2blacklist_local(user, email):
    if _check_add_blacklist(user, email):
        # insert the email to block in the user's blacklist
        blacklist = Blacklist()
        blacklist.add_blocked_user(user, email)
        db.session.add(blacklist)
        db.session.commit()


def is_blacklisted(sender, receiver):
    return db.session.query(
        Blacklist.query.filter(
            Blacklist.email == sender,
            Blacklist.owner == receiver).exists()).scalar()
