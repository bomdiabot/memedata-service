from flask_restful import Resource

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)

from webargs import validate
from webargs.flaskparser import parser
from webargs.fields import (
    Str,
)

from flask import (
    request,
    abort,
)

from memedata.util import (
    mk_errors,
    mk_message,
    fmt_validation_error_messages,
    flatten,
    filter_fields,
)

from memedata.models import User, RevokedToken
from memedata.database import db
from memedata.extensions import jwt

from passlib.hash import pbkdf2_sha256 as sha256

_USER_PASS_ARGS = {
    'username': Str(required=True),
    'password': Str(validate=validate.Length(min=8), required=True),
}

def generate_hash(password):
    return sha256.hash(password)

def verify_hash(password, hsh):
    return sha256.verify(password, hsh)

class Login(Resource):
    def post(self):
        args = parser.parse(_USER_PASS_ARGS, request)

        user = User.query.filter_by(username=args['username']).first()
        if user is None or not verify_hash(args['password'], user.password):
            return mk_errors(400, 'invalid username or password')

        access_tok = create_access_token(identity=args['username'])
        refresh_tok = create_refresh_token(identity=args['username'])

        return {
            'message': 'user "{}" logged in'.format(args['username']),
            'access_token': access_tok,
            'refresh_token': refresh_tok,
        }

class UserRes(Resource):
    @jwt_required
    def get(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            return mk_errors(404, 'user id={} does not exist'.format(user_id))
        return {'user': user.to_json()}

    @jwt_required
    def delete(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            return mk_errors(404, 'user id={} does not exist'.format(user_id))
        db.session.delete(user)
        db.session.commit()
        return '', 204

class UsersRes(Resource):
    @jwt_required
    def get(self):
        users = User.query.all()
        return {'users': [u.to_json() for u in users]}

    def post(self):
        args = parser.parse(_USER_PASS_ARGS, request)

        if User.query.filter_by(username=args['username']).first():
            return mk_errors(
                400, 'username "{}" already taken'.format(args['username']))
        new_user = User(
            username=args['username'],
            password=generate_hash(args['password'])
        )
        new_user.save()

        access_tok = create_access_token(identity=args['username'])
        refresh_tok = create_refresh_token(identity=args['username'])

        return {
            'message': 'user "{}" created'.format(args['username']),
            'access_token': access_tok,
            'refresh_token': refresh_tok,
            'user_id': int(new_user.user_id),
        }

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)

class LogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.save()
            return mk_message('access token revoked')
        except:
            raise
            return mk_errors(500, 'error in logout')

class LogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.save()
            return mk_message('refresh token revoked')
        except:
            return mk_errors('error in logout')

class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'd': ':^)'
        }
