#!/usr/bin/env python3

from flask import (
    Flask,
)
from flask_restful import (
    Api,
)

from .images import Image, Images
from .texts import Text, Texts

def get_app():
    app = Flask(__name__)
    return app

def get_api(app):
    api = Api(app)
    api.add_resource(Image, '/images/<int:uid>')
    api.add_resource(Images, '/images')
    api.add_resource(Text, '/texts/<int:uid>')
    api.add_resource(Texts, '/texts')
    return api

def main():
    app = get_app()
    api = get_api(app)
    app.run()

if __name__ == '__main__':
    main()
