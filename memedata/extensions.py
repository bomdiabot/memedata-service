from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager

db = SQLAlchemy()

jwt = JWTManager()

from memedata.resources import texts, images, auth
api = Api()
#texts
api.add_resource(texts.TextsRes, '/texts')
api.add_resource(texts.TextRes, '/texts/<int:uid>')
#images
api.add_resource(images.ImagesRes, '/images')
api.add_resource(images.ImageRes, '/images/<int:uid>')
#auth
api.add_resource(auth.Login, '/users/login')
api.add_resource(auth.UserRes, '/users/<int:user_id>')
api.add_resource(auth.UsersRes, '/users')
api.add_resource(auth.TokenRefresh, '/users/token/refresh')
api.add_resource(auth.LogoutAccess, '/users/logout/access')
api.add_resource(auth.LogoutRefresh, '/users/logout/refresh')
api.add_resource(auth.SecretResource, '/secret')
