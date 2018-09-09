#!/usr/bin/env python3

from flask import (
    Flask,
)
from flask_restful import (
    Api,
)

from .images import Image, Images
from .texts import TextRes, TextsRes
from .database import session as db, DB_PATH

DEBUG = not True

def get_app():
    app = Flask('memedata-service')

    #db stuff
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH 
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
    app.run(debug=DEBUG)

if __name__ == '__main__':
    main()
