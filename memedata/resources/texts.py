import datetime as dt

from flask import (
    request,
    abort,
)
from flask_restful import (
    Resource,
)
from marshmallow import (
    ValidationError,
)

from memedata.models import Text
from memedata.serializers import TextSchema
from memedata.database import db
from memedata.util import mk_errors, fmt_validation_error_messages

class TextRes(Resource):
    @staticmethod
    def get_text(uid):
        text = Text.query.get(uid)
        if text is None:
            abort(mk_errors(404, '{} doest not exist'.format(uid)))
        return text

    def get(self, uid):
        text = TextRes.get_text(uid)
        return TextSchema().dump(text)

    def put(self, uid):
        text = TextRes.get_text(uid)
        try:
            schema = TextSchema()
            text = schema.load(request.values, instance=text, partial=True)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        db.session.add(text)
        db.session.commit()
        return schema.dump(text)

    def delete(self, uid):
        text = TextRes.get_text(uid)
        db.session.delete(text)
        db.session.commit()
        return '', 204

class TextsRes(Resource):
    def post(self):
        try:
            text = TextSchema().load(request.values)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        db.session.add(text)
        db.session.commit()
        return TextSchema().dump(text), 201

    def get(self):
        return TextSchema(many=True).dump(Text.query.all())
