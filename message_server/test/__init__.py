import logging

import connexion
from flask_testing import TestCase

from message_server.encoder import JSONEncoder
from message_server.database import db


class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        _APP = app.app
        _APP.json_encoder = JSONEncoder
        app.add_api('swagger.yaml')
        _APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../T_message.db'
        db.init_app(_APP)
        db.create_all(app=_APP)
        return _APP
