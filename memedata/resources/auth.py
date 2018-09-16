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
    generate_hash,
    verify_hash,
)

from memedata.models import User, RevokedToken
from memedata.database import db
from memedata.extensions import jwt
from memedata import config

_USER_PASS_ARGS = {
    'username': Str(required=True),
    'password': Str(
        validate=validate.Length(min=config.min_password_len), required=True),
}

def check_priviledges():
    if not get_jwt_identity() in config.superusers:
        abort(401, 'unauthorized user')

class Login(Resource):
    def post(self):
        """
        Login into system.

        .. :quickref: Login; User login.

        **Example request**:

        .. sourcecode:: http

	    POST /auth/login HTTP/1.1
	    Host: example.com
	    Accept: application/json

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 200 OK
	    Content-Type: application/json

            {
                "message": "user 'jose' logged in",
                "access_token": "lajdfh09l8valufd89y614b",
                "refresh_token": "lkjahdljxoiuhqdouifhob"
            }


        :form username: the user name (required)
        :form password: the user password (required)
        :resheader Content-Type: application/json
        :status 200: user logged in
        """
        args = parser.parse(_USER_PASS_ARGS, request,
            locations=('form', 'json'))

        user = User.query.filter_by(username=args['username']).first()
        if user is None or not verify_hash(args['password'], user.password):
            return mk_errors(400, 'invalid username or password')

        access_tok = create_access_token(identity=args['username'])
        refresh_tok = create_refresh_token(identity=args['username'])

        return {
            'message': 'user \'{}\' logged in'.format(args['username']),
            'access_token': access_tok,
            'refresh_token': refresh_tok,
        }

class UserRes(Resource):
    @jwt_required
    def get(self, user_id):
        """
        Get user. Only priviledged users can use this method.

        .. :quickref: Get user; Get user.

        **Example request**:

        .. sourcecode:: http

	    GET /users/1 HTTP/1.1
	    Host: example.com
	    Accept: application/json
	    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhb

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 200 OK
	    Content-Type: application/json

            {
                "user": {
                    "user_id": 1,
                    "password": "$pbkdf2-sha256$29000$7kp6XipQ",
                    "username": "su"
                }
            }


        :reqheader Authorization: access token of logged in user (required)
        :param int user_id: id of user.
        :resheader Content-Type: application/json
        :status 200: user found
        """
        check_priviledges()
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            return mk_errors(404, 'user id={} does not exist'.format(user_id))
        return {'user': user.to_json()}

    @jwt_required
    def delete(self, user_id):
        """
        Delete user. Only priviledged users can use this method.

        .. :quickref: Delete user; Delete user.

        **Example request**:

        .. sourcecode:: http

	    DELETE /users/1 HTTP/1.1
	    Host: example.com
	    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhb

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 204 NO CONTENT


        :reqheader Authorization: access token of logged in user (required)
        :param int user_id: id of user.
        :status 204: user deleted
        """
        check_priviledges()
        user = User.query.filter_by(user_id=user_id).first()
        if user is None:
            return mk_errors(404, 'user id={} does not exist'.format(user_id))
        db.session.delete(user)
        db.session.commit()
        return '', 204

class UsersRes(Resource):
    @jwt_required
    def get(self):
        """
        Get users. Only priviledged users can use this method.

        .. :quickref: Get users; Get users.

        **Example request**:

        .. sourcecode:: http

	    GET /users HTTP/1.1
	    Host: example.com
	    Accept: application/json
	    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhb

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 200 OK
	    Content-Type: application/json

            {
                "users": [
                    {
                        "user_id": 1,
                        "password": "$pbkdf2-sha256$29000$7kp6XipQ",
                        "username": "su"
                    },
                    {
                        "user_id": 2,
                        "password": "$pbkdf2-sha256$29000$8adovub",
                        "username": "maria"
                    }
                ]
            }


        :reqheader Authorization: access token of logged in user (required)
        :resheader Content-Type: application/json
        :status 200: users found
        """
        check_priviledges()
        users = User.query.all()
        return {'users': [u.to_json() for u in users]}

    @jwt_required
    def post(self):
        """
        Create user. Only priviledged users can use this method.

        .. :quickref: Create user; Create user.

        **Example request**:

        .. sourcecode:: http

	    POST /users HTTP/1.1
	    Host: example.com
	    Accept: application/json
	    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhb

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 201 CREATED
	    Content-Type: application/json

            {
                "user_id": 1,
                "message": "user 'joao' created"
            }


        :reqheader Authorization: access token of logged in user (required)
        :resheader Content-Type: application/json
        :status 201: user created
        """
        check_priviledges()
        args = parser.parse(_USER_PASS_ARGS, request,
            locations=('form', 'json'))

        if User.query.filter_by(username=args['username']).first():
            return mk_errors(
                400, 'username \'{}\' already taken'.format(args['username']))
        new_user = User.create_and_save(args['username'], args['password'])

        return {
            'message': 'user \'{}\' created'.format(args['username']),
            'user_id': int(new_user.user_id),
        }, 201

class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        """
        Refresh access token.

        .. :quickref: Refresh token; Refresh access token.

        **Example request**:

        .. sourcecode:: http

	    POST /auth/token/refresh HTTP/1.1
	    Host: example.com
	    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhb

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 200 OK
	    Content-Type: application/json

            {
                "access_token": "lajdfh09l8valufd89y614b"
            }

        :reqheader Authorization: refresh token of logged in user (required)
        :status 200: token refreshed
        """
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
        """
        Revoke access token.

        .. :quickref: Access Logout; Revoke access token.

        **Example request**:

        .. sourcecode:: http

	    POST /auth/logout/access HTTP/1.1
	    Host: example.com
	    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhb

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 204 NO CONTENT

        :reqheader Authorization: access token of logged in user (required)
        :status 204: user logged out
        """
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.save()
            return '', 204
        except:
            raise
            return mk_errors(500, 'error in logout')

class LogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        """
        Revoke refresh token.

        .. :quickref: Refresh Logout; Revoke refresh token.

        **Example request**:

        .. sourcecode:: http

	    POST /auth/logout/refresh HTTP/1.1
	    Host: example.com
	    Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhb

        **Example response**:

        .. sourcecode:: http

	    HTTP/1.1 204 NO CONTENT

        :reqheader Authorization: refresh token of logged in user (required)
        :status 204: token revoked
        """
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.save()
            return '', 204
        except:
            return mk_errors('error in logout')

class Ok(Resource):
    @jwt_required
    def get(self):
        return mk_message('ok')
