#!/usr/bin/env python3

from flask import (
    Flask,
)
from flask_restful import (
    Api,
)

from images import Image, Images
from texts import Text, Texts

app = Flask(__name__)
api = Api(app)

api.add_resource(Image, '/images/<int:uid>')
api.add_resource(Images, '/images')
api.add_resource(Text, '/texts/<int:uid>')
api.add_resource(Texts, '/texts')

if __name__ == '__main__':
    app.run(debug=True)
