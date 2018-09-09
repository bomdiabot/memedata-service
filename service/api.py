#!/usr/bin/env python3

from flask import (
    Flask,
)
from flask_restful import (
    Api,
)

from service.images import Image, Images
from service.texts import TextRes, TextsRes
from service.database import session as db
from service import config

def get_app():
    app = Flask('memedata-service')

    #configuration
    app.config.update(config.flask_app_config)

    #db stuff
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.remove()

    return app

def get_api(app):
    api = Api(app)
    api.add_resource(Image, '/images/<int:uid>')
    api.add_resource(Images, '/images')
    api.add_resource(TextRes, '/texts/<int:uid>')
    api.add_resource(TextsRes, '/texts')
    return api

def main():
    app = get_app()
    api = get_api(app)
    app.run(debug=config.debug)

if __name__ == '__main__':
    main()
