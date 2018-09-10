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
    EXCLUDE,
)

from memedata.util import (
    mk_errors,
    fmt_validation_error_messages,
)

import datetime as dt
import shutil
import tempfile
import os

IMAGES_DIR_PATH = os.path.join(tempfile.gettempdir(), 'images_db_ad8b29mc1')
if os.path.isdir(IMAGES_DIR_PATH):
    shutil.rmtree(IMAGES_DIR_PATH)
os.makedirs(IMAGES_DIR_PATH)
DB = {}

VALID_MIMETYPES = {'image/jpeg', 'image/png'}

class ImageDao:
    def __init__(self, uid):
        self.uid = uid
        self.created_at = dt.datetime.now()
        self.modified_at = self.created_at

    def __repr__(self):
        return 'Image(uid={})'.format(self.uid)

class ImageSchema(Schema):
    uid = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = EXCLUDE

    @staticmethod
    def get_envelope_key(many):
        return 'images' if many else 'image'

    @post_dump(pass_many=True)
    def envelope(self, dct, many):
        return {ImageSchema.get_envelope_key(many): dct}

def _get_uids():
    return set(DB.keys())

def _get_path(uid, mimetype):
    ext = 'jpg' if mimetype == 'image/jpeg' else 'png'
    return os.path.join(IMAGES_DIR_PATH, '{}.{}'.format(uid, ext))

def _exists(uid):
    return uid in DB.keys()

class ImageRes(Resource):
    def get(self, uid):
        if not _exists(uid):
            return mk_errors(404, '{} does not exist'.format(uid))

        for mt, __ in request.accept_mimetypes:
            if mt in VALID_MIMETYPES:
                return send_file(_get_path(uid, mt), mt)
        else:
            return ImageSchema().dump(DB[uid])

    def put(self, uid):
        if not _exists(uid):
            return mk_errors(404, '{} does not exist'.format(uid))

        data = request.files.get('image')
        if data is None:
            return mk_errors(400, 'image file not present')
        elif data.mimetype not in VALID_MIMETYPES:
            return mk_errors(400, 'wrong file format (must be png or jpg)')
        else:
            for mt in VALID_MIMETYPES:
                path = _get_path(uid, mt)
                if os.path.isfile(path):
                    break
            else:
                raise
            data.save(path)
            DB[uid].modified_at = dt.datetime.now()
            return ImageSchema().dump(DB[uid]), 200

    def delete(self, uid):
        if not _exists(uid):
            return mk_errors(404, '{} does not exist'.format(uid))

        for mt in VALID_MIMETYPES:
            path = _get_path(uid, mt)
            if os.path.isfile(path):
                break
        else:
            return mk_errors(500, 'internal error')

        os.remove(path)
        del DB[uid]
        return '', 204

class ImagesRes(Resource):
    def post(self):
        data = request.files.get('image')
        if data is None:
            return mk_errors(400, 'image file not present')
        elif data.mimetype not in VALID_MIMETYPES:
            return mk_errors(400, 'wrong file format (must be png or jpg)')
        else:
            uid = max(_get_uids(), default=0) + 1
            path = _get_path(uid, data.mimetype)
            data.save(path)
            obj = ImageDao(uid)
            DB[uid] = obj
            return ImageSchema().dump(obj), 201

    def get(self):
        return ImageSchema(many=True).dump(DB.values())
