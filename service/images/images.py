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

def mk_errors(errors, code=400):
    if not isinstance(errors, list):
        errors = [errors]
    return {'errors': errors}, code

class Image(Resource):
    def get(self, uid):
        if not _exists(uid):
            return mk_errors('{} doest not exist'.format(uid))

        if not request.mimetype or request.mimetype == 'application/json':
            return ImageSchema().dump(DB[uid])
        elif request.mimetype in VALID_MIMETYPES:
            return send_file(_get_path(uid, request.mimetype), request.mimetype)
        else:
            return mk_errors(
                '"{}" is not a valid mimetype for request'.format(
                    request.mimetype))

    def put(self, uid):
        if not _exists(uid):
            return mk_errors('{} existn\'t'.format(uid))

        data = request.files.get('image')
        if data is None:
            return mk_errors('image file not present')
        elif data.mimetype not in VALID_MIMETYPES:
            return mk_errors('wrong file format (must be png or jpg)')
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
            return mk_errors('{} does not exist'.format(uid))

        for mt in VALID_MIMETYPES:
            path = _get_path(uid, mt)
            if os.path.isfile(path):
                break
        else:
            raise

        os.remove(path)
        del DB[uid]
        return '', 200

class Images(Resource):
    def post(self):
        data = request.files.get('image')
        if data is None:
            return mk_errors('image file not present')
        elif data.mimetype not in VALID_MIMETYPES:
            return mk_errors('wrong file format (must be png or jpg)')
        else:
            uid = max(_get_uids(), default=0) + 1
            path = _get_path(uid, data.mimetype)
            data.save(path)
            obj = ImageDao(uid)
            DB[uid] = obj
            return ImageSchema().dump(obj), 200

    def get(self):
        return ImageSchema(many=True).dump(DB.values())
