from flask import (
    request,
    send_file,
)

from flask_restful import (
    Resource,
    abort,
)

from marshmallow import (
    Schema,
    fields,
    ValidationError,
    post_dump,
)

import datetime as dt

DB = {}

class TextDao:
    def __init__(self, uid, content=''):
        self.uid = uid
        self.content = content
        self.created_at = dt.datetime.now()
        self.modified_at = self.created_at

    def __repr__(self):
        return 'Text(uid={}, content={})'.format(self.uid, self.content)

class TextSchema(Schema):
    uid = fields.Integer(dump_only=True)
    content = fields.String(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)

    @staticmethod
    def get_envelope_key(many):
        return 'texts' if many else 'text'

    @post_dump(pass_many=True)
    def envelope(self, dct, many):
        return {TextSchema.get_envelope_key(many): dct}

def _get_uids():
    return set(DB.keys())

def _exists(uid):
    return uid in DB.keys()

def mk_errors(errors, code=400):
    if not isinstance(errors, list):
        errors = [errors]
    return {'errors': errors}, code

class Text(Resource):
    def get(self, uid):
        if not _exists(uid):
            return mk_errors('{} doest not exist'.format(uid))
        return TextSchema().dump(DB[uid])

    def put(self, uid):
        if not _exists(uid):
            return mk_errors('{} existn\'t'.format(uid))

        try:
            dct = TextSchema().load(request.form)
        except ValidationError as e:
            return mk_errors({'ValidationError': e.messages})

        for k, v in dct.items():
            setattr(DB[uid], k, v)
        DB[uid].modified_at = dt.datetime.now()
        return TextSchema().dump(DB[uid])

    def delete(self, uid):
        if not _exists(uid):
            return mk_errors('{} does not exist'.format(uid))
        del DB[uid]
        return '', 200

class Texts(Resource):
    def post(self):
        try:
            dct = TextSchema().load(request.values)
        except ValidationError as e:
            return mk_errors({'ValidationError': e.messages})
        uid = max(_get_uids(), default=0) + 1
        DB[uid] = TextDao(uid, **dct)
        return TextSchema().dump(DB[uid])

    def get(self):
        return TextSchema(many=True).dump(DB.values())
