from flask import (
    request,
    send_file,
    abort,
)

from flask_restful import (
    Resource,
)

from marshmallow import (
    Schema,
    fields,
    ValidationError,
    post_dump,
    EXCLUDE,
)

from service.util import (
    mk_errors,
    fmt_validation_error_messages,
)

from service.database import (
    session as db,
)

from service.models import (
    Text,
)

from marshmallow_sqlalchemy import (
    ModelSchema,
    field_for,
)

import datetime as dt

class TextSchema(ModelSchema):
    content = field_for(Text, 'content', required=True)
    created_at = field_for(Text, 'created_at', dump_only=True)
    updated_at = field_for(Text, 'updated_at', dump_only=True)

    class Meta:
        unknown = EXCLUDE
        model = Text
        sqla_session = db

    @staticmethod
    def get_envelope_key(many):
        return 'texts' if many else 'text'

    @post_dump(pass_many=True)
    def envelope(self, dct, many):
        return {TextSchema.get_envelope_key(many): dct}

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
        db.add(text)
        db.commit()
        return schema.dump(text)

    def delete(self, uid):
        text = TextRes.get_text(uid)
        db.delete(text)
        db.commit()
        return '', 204

class TextsRes(Resource):
    def post(self):
        try:
            text = TextSchema().load(request.values)
        except ValidationError as e:
            return mk_errors(400, fmt_validation_error_messages(e.messages))
        db.add(text)
        db.commit()
        return TextSchema().dump(text), 201

    def get(self):
        return TextSchema(many=True).dump(Text.query.all())
