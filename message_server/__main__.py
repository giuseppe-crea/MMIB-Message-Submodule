#!/usr/bin/env python3

import connexion

from message_server import encoder
from flask_uploads import UploadSet, IMAGES, configure_uploads
from message_server.database import db
import message_server.tasks as celery_module


images = UploadSet('images', IMAGES, default_dest=None)
_APP = None


def main():
    global _APP
    app = connexion.App(__name__, specification_dir='./swagger/')
    _APP = app.app
    _APP.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Messages'})
    _APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../message.db'
    _APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # configure_uploads(app.app, images)
    db.init_app(_APP)
    db.create_all(app=_APP)
    celery_module.give_context(_APP)
    app.run(port=4000)


if __name__ == '__main__':
    main()
