from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

db = SQLAlchemy()

from memedata.resources import texts, images
api = Api()
api.add_resource(texts.TextsRes, '/texts')
api.add_resource(texts.TextRes, '/texts/<int:uid>')
api.add_resource(images.ImagesRes, '/images')
api.add_resource(images.ImageRes, '/images/<int:uid>')
