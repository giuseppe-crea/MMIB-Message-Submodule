from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_email = db.Column(db.Unicode(128), nullable=False)
    receiver_email = db.Column(db.Unicode(1028), nullable=False)
    message = db.Column(db.Unicode(1024), nullable=False)
    # for ease of use with Celery, we import this as string
    # format: "%Y-%M-%D %H:%M:%s" on GMT+1
    time = db.Column(db.Unicode(128), nullable=False)
    image = db.Column(db.Unicode(1024), nullable=False)
    image_hash = db.Column(db.Unicode(2000000), nullable=True)
    # 0 draft, 1 sent, 2 delivered
    status = db.Column(db.Integer, nullable=False)
    # two columns: visible to sender, visible to receiver, for deletion
    # when both are set to false, the message is deleted
    visible_to_sender = db.Column(db.Boolean, nullable=False)
    visible_to_receiver = db.Column(db.Boolean, nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    def __init__(self, *args, **kw):
        super(Message, self).__init__(*args, **kw)

    def add_message(self, message, sender_email, receiver_email, time, image,
                    image_hash, status, visible_to_receiver=True):
        """
        adds a message to database, initializing to empty all missing fields
        """
        if message is not None:
            self.message = message
        else:
            self.message = ''
        self.sender_email = sender_email
        if receiver_email is not None:
            self.receiver_email = receiver_email
        else:
            self.receiver_email = ''
        if time is not None:
            self.time = time
        else:
            self.time = ''
        if image is not None and image != '':
            self.image = image
            self.image_hash = image_hash
        else:
            self.image = ''
            self.image_hash = ''
        self.status = status
        self.visible_to_sender = True
        if not visible_to_receiver:
            self.visible_to_receiver = False
        else:
            self.visible_to_receiver = True
        self.is_read = False

    def get_id(self):
        """
        :return: message id for this object
        """
        return self.id

    def get_status(self):
        """
        :return: message status for this object
        """
        return self.status


class Blacklist(db.Model):
    __tablename__ = 'blacklist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Unicode(128), nullable=False)
    email = db.Column(db.Unicode(128), nullable=False)

    def __init__(self, *args, **kw):
        super(Blacklist, self).__init__(*args, **kw)

    def add_blocked_user(self, owner, email):
        self.owner = owner
        self.email = email

    def get_id(self):
        return self.owner
